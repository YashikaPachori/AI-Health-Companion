
from django.contrib import admin
from .models import Consultation, ChatMessage, DoctorRating

@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'status', 'consultation_date', 'created_at']
    list_filter = ['status', 'consultation_date', 'created_at']
    search_fields = ['patient__user__username', 'doctor__user__username']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['consultation', 'sender', 'message_preview', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['sender__username', 'message']
    readonly_fields = ['created_at']
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'

@admin.register(DoctorRating)
class DoctorRatingAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['patient__user__username', 'doctor__user__username']
    readonly_fields = ['created_at']
# Register your models here.
