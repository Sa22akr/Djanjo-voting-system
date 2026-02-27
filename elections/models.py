from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import secrets
import hashlib


# =====================
# Election
# =====================

class Election(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name


# =====================
# Position
# =====================

class Position(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.title} - {self.election.name}"


# =====================
# Profile
# =====================

class Profile(models.Model):
    ROLE_CHOICES = (
        ('voter', 'Voter'),
        ('candidate', 'Candidate'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    position = models.ForeignKey(
    Position,
    on_delete=models.SET_NULL,
    null=True,
    blank=True
    )

    photo = models.ImageField(upload_to='candidate_photos/', null=True, blank=True)


    def __str__(self):
        return f"{self.user.username} - {self.role}"


# =====================
# Candidate
# =====================

class Candidate(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# =====================
# Vote
# =====================

class Vote(models.Model):
    voter = models.ForeignKey(User, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE, null=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Profile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    hash_value = models.CharField(max_length=64, editable=False)

    def save(self, *args, **kwargs):
        if not self.hash_value:
            raw = f"{self.voter.id}{self.candidate.id}{timezone.now()}"
            self.hash_value = hashlib.sha256(raw.encode()).hexdigest()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('voter', 'position')


# =====================
# CandidateKey
# =====================

class CandidateKey(models.Model):
    key_code = models.CharField(max_length=50, unique=True, editable=False)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.key_code:
            self.key_code = secrets.token_hex(8).upper()
        super().save(*args, **kwargs)

    def is_valid(self):
        return (
            not self.used and
            timezone.now() < self.expires_at and
            self.election.is_active
        )

    def __str__(self):
        return f"{self.key_code} ({self.position.title})"


# =====================
# Audit Log
# =====================

class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True)