"""Admin registration for the RMS models."""

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Company, ResumeEntry, UserResume


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "approval_status", "submitted_at", "admin_review_link")
    list_filter = ("approval_status", "submitted_at")
    search_fields = ("name", "user__username", "user__email")
    list_select_related = ("user",)
    actions = ("approve_selected", "reject_selected")

    @admin.display(description="Review companies")
    def admin_review_link(self, obj):
        return format_html('<a href="{}">Open review queue</a>', reverse("review_queue"))

    @admin.action(description="Approve selected companies")
    def approve_selected(self, request, queryset):
        updated = queryset.update(approval_status="approved")
        self.message_user(request, f"{updated} company(ies) approved.")

    @admin.action(description="Reject selected companies")
    def reject_selected(self, request, queryset):
        updated = queryset.update(approval_status="rejected")
        self.message_user(request, f"{updated} company(ies) rejected.")


@admin.register(UserResume)
class UserResumeAdmin(admin.ModelAdmin):
    list_display = ("id", "filename", "top_role", "uploaded_at")
    search_fields = ("extracted_text", "prediction")
    readonly_fields = ("extracted_text", "prediction", "uploaded_at")
    date_hierarchy = "uploaded_at"

    @admin.display(description="File")
    def filename(self, obj):
        return obj.filename

    @admin.display(description="Top role")
    def top_role(self, obj):
        return obj.top_role


@admin.register(ResumeEntry)
class ResumeEntryAdmin(admin.ModelAdmin):
    list_display = ("id", "uploaded_at", "resume_hash")
    search_fields = ("resume_hash", "extracted_text")
    readonly_fields = ("resume_hash", "extracted_text", "uploaded_at")
    date_hierarchy = "uploaded_at"
