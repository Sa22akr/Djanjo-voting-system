from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import HttpResponse
from django.utils import timezone

from .models import Candidate, Vote, Profile, CandidateKey, Election
from .forms import RegisterForm


def home(request):
    return render(request, "elections/home.html")


def register(request):
    from django.utils import timezone

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            role = form.cleaned_data["role"]
            key = form.cleaned_data.get("candidate_key")

            # If candidate, validate key FIRST
            if role == "candidate":

                if not key:
                    return render(request, "elections/register.html", {
                        "form": form,
                        "error": "Candidate key is required."
                    })

                try:
                    candidate_key = CandidateKey.objects.get(
                        key_code=key,
                        used=False
                    )
                except CandidateKey.DoesNotExist:
                    return render(request, "elections/register.html", {
                        "form": form,
                        "error": "Invalid or already used candidate key."
                    })

                # Check expiry
                if timezone.now() > candidate_key.expires_at:
                    return render(request, "elections/register.html", {
                        "form": form,
                        "error": "Candidate key has expired."
                    })

            # Now create user safely
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()

            profile = Profile.objects.create(
                user=user,
                role=role
            )

            # If candidate, assign position + mark key used
            if role == "candidate":
                profile.position = candidate_key.position
                profile.save()

                candidate_key.used = True
                candidate_key.save()

            login(request, user)
            return redirect("home")

    else:
        form = RegisterForm()

    return render(request, "elections/register.html", {"form": form})

@login_required
def vote(request):
    from django.utils import timezone
    from .models import Election, Position, Profile, Vote

    # Get active election
    election = Election.objects.filter(is_active=True).first()

    if not election:
        return render(request, "elections/error.html", {
            "message": "No active election."
        })

    # Check election window
    if not (election.start_date <= timezone.now() <= election.end_date):
        return render(request, "elections/error.html", {
            "message": "Voting window is closed."
        })

    # Get or create profile
    profile, created = Profile.objects.get_or_create(
        user=request.user,
        defaults={"role": "voter"}
    )

    # Block candidates from voting
    if profile.role == "candidate":
        return render(request, "elections/candidate_dashboard.html", {
            "profile": profile
        })

    # Prevent double voting
    if Vote.objects.filter(voter=request.user, election=election).exists():
        return render(request, "elections/already_voted.html", {
            "message": "You have already voted."
        })

    positions = Position.objects.filter(election=election)

    # Attach candidates to each position
    for position in positions:
        position.candidates = Profile.objects.filter(
            role="candidate",
            position=position
        )

    # Handle form submission
    if request.method == "POST":
        for position in positions:
            candidate_id = request.POST.get(f"position_{position.id}")

            if not candidate_id:
                return render(request, "elections/error.html", {
                    "message": "You must select a candidate for every position."
                })

            candidate = Profile.objects.get(
                id=candidate_id,
                role="candidate"
            )

            Vote.objects.create(
                voter=request.user,
                election=election,
                position=position,
                candidate=candidate
            )

        return render(request, "elections/success.html")

    # GET request — show voting page
    return render(request, "elections/vote.html", {
        "election": election,
        "positions": positions
    })

@login_required
def results(request):
    candidates = Profile.objects.filter(role="candidate")
    total_votes = Vote.objects.count()
    results = []

    election = Election.objects.filter(is_active=True).first()

    if election and timezone.now() <= election.end_date:
        return render(request, "elections/error.html", {
            "election": election,
            "message": "Results are not available until voting has closed."
        })

    for candidate in candidates:
        vote_count = Vote.objects.filter(candidate=candidate).count()

        percentage = 0
        if total_votes > 0:
            percentage = int((vote_count / total_votes) * 100)

        results.append({
            "profile": candidate,   # ✅ FIXED
            "count": vote_count,
            "percentage": percentage,
        })

    return render(request, "elections/results.html", {
        "results": results,
        "total_votes": total_votes
    })