from django.contrib import admin

from .forms import MemberForm
from .models import Member

class MemberAdmin(admin.ModelAdmin):

    form = MemberForm

    fieldsets = [
        (
            "Login Details",
            {
                "fields": (
                    "username",
                    "password",
                    ("first_name", "last_name"),
                    "is_active",
                    "email",
                ),
            }
        ),
        (
            "Roles",
            {
                "fields": (
                    "groups",
                    ("is_datascientist", "is_annotator"),
                )
            }
        ),

    ]
    # readonly_fields = ["password", ]
    list_display = [
        "id", "username", "is_datascientist", "is_annotator", "first_name",
        "last_name", "is_active"
    ]
    list_filter = ["is_annotator", "is_datascientist"]


admin.site.register(Member, MemberAdmin)
