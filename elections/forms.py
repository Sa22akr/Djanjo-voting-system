from django import forms
from django.contrib.auth.models import User
from .models import Profile, CandidateKey

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES)
    candidate_key = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ['username', 'password']

    from django.utils import timezone

def clean(self):
    cleaned_data = super().clean()
    role = cleaned_data.get("role")
    key = cleaned_data.get("candidate_key")

    if role == "candidate":
        if not key:
            raise forms.ValidationError("Candidate key is required.")

        try:
            candidate_key = CandidateKey.objects.get(key_code=key)
        except CandidateKey.DoesNotExist:
            raise forms.ValidationError("Invalid candidate key.")

        if not candidate_key.is_valid():
            raise forms.ValidationError("Key expired, used, or election inactive.")

    return cleaned_data