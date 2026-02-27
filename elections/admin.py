from django.contrib import admin
from django.utils import timezone
from datetime import timedelta
from .models import Candidate, Vote, Profile, CandidateKey, Election, Position


# ======================
# Election
# ======================

@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "start_date", "end_date")


# ======================
# Position
# ======================

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ("title", "election")


# ======================
# Candidate Key
# ======================

@admin.register(CandidateKey)
class CandidateKeyAdmin(admin.ModelAdmin):
    list_display = ("key_code", "position", "election", "used", "expires_at")
    list_filter = ("used", "election")
    actions = ["generate_keys"]

    def generate_keys(self, request, queryset):
        for obj in queryset:
            for _ in range(5):
                CandidateKey.objects.create(
                    election=obj.election,
                    position=obj.position,
                    expires_at=timezone.now() + timedelta(days=7)
                )
    generate_keys.short_description = "Generate 5 keys for selected rows"


# ======================
# Simple Registrations
# ======================

admin.site.register(Profile)
admin.site.register(Candidate)
admin.site.register(Vote)