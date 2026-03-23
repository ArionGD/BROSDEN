from django.contrib import admin
from .models import PropertyReview, TenantReview

@admin.register(PropertyReview)
class PropertyReviewAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'property', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('tenant__username', 'property__title', 'comment')

@admin.register(TenantReview)
class TenantReviewAdmin(admin.ModelAdmin):
    list_display = ('owner', 'tenant', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('owner__username', 'tenant__username', 'comment')
