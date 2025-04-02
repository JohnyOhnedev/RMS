from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "approval_status", "admin_review_link")
    
    def admin_review_link(self, obj):
        # This will create a link to the review_queue page.
        return format_html('<a href="{}">Review Queue</a>', reverse("review_queue"))

    admin_review_link.short_description = "Review Companies"
