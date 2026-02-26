from django.contrib import admin
from .models import Contract, ContractTemplate

@admin.register(ContractTemplate)
class ContractTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('booking', 'created_at', 'is_signed_by_tenant', 'is_signed_by_owner')
    list_filter = ('is_signed_by_tenant', 'is_signed_by_owner')
