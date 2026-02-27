
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Candidate, Vote

@login_required
def vote(request):
    if Vote.objects.filter(user=request.user).exists():
        return render(request, 'elections/already_voted.html')

    if request.method == 'POST':
        candidate_id = request.POST.get('candidate')
        candidate = Candidate.objects.get(id=candidate_id)
        Vote.objects.create(user=request.user, candidate=candidate)
        return redirect('results')

    candidates = Candidate.objects.all()
    return render(request, 'elections/vote.html', {'candidates': candidates})

@login_required
def results(request):
    candidates = Candidate.objects.all()
    results = []
    for candidate in candidates:
        count = Vote.objects.filter(candidate=candidate).count()
        results.append((candidate.name, count))
    return render(request, 'elections/results.html', {'results': results})
