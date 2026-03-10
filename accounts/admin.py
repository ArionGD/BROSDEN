from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, KYC, ProMembership, ProFeature

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'email', 'role', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role', 'phone_number', 'profile_photo')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Information', {'fields': ('role', 'phone_number')}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(KYC)
admin.site.register(ProMembership)
admin.site.register(ProFeature)
