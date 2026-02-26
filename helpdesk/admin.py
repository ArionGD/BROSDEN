from django.contrib import admin
from .models import Category, Ticket, TicketReply

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')

class TicketReplyInline(admin.TabularInline):
    model = TicketReply
    extra = 1

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'user', 'status', 'priority', 'created_at')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('subject', 'description', 'user__username')
    inlines = [TicketReplyInline]
