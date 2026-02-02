from django.contrib import admin

from .models import (Disease, Symptom, DiseasePrecaution, DiseaseDiet, 
                     DiseaseExercise, DiseaseMedicine, PredictionHistory,
                     CustomSymptomSuggestion)

@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'severity_level', 'specialist_required', 'created_at']
    list_filter = ['severity_level', 'specialist_required']
    search_fields = ['name', 'description']

@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(DiseasePrecaution)
class DiseasePrecautionAdmin(admin.ModelAdmin):
    list_display = ['disease', 'priority', 'precaution']
    list_filter = ['disease']
    ordering = ['disease', 'priority']

@admin.register(DiseaseDiet)
class DiseaseDietAdmin(admin.ModelAdmin):
    list_display = ['disease', 'food_item', 'is_recommended']
    list_filter = ['disease', 'is_recommended']
    search_fields = ['food_item']

@admin.register(DiseaseExercise)
class DiseaseExerciseAdmin(admin.ModelAdmin):
    list_display = ['disease', 'exercise_name', 'intensity', 'duration']
    list_filter = ['disease', 'intensity']
    search_fields = ['exercise_name']

@admin.register(DiseaseMedicine)
class DiseaseMedicineAdmin(admin.ModelAdmin):
    list_display = ['disease', 'medicine_name', 'dosage', 'priority']
    list_filter = ['disease']
    search_fields = ['medicine_name', 'generic_name']
    ordering = ['disease', 'priority']

@admin.register(PredictionHistory)
class PredictionHistoryAdmin(admin.ModelAdmin):
    list_display = ['patient', 'predicted_disease', 'confidence_score', 'consulted_doctor', 'created_at']
    list_filter = ['predicted_disease', 'consulted_doctor', 'created_at']
    search_fields = ['patient__user__username']
    readonly_fields = ['created_at']

@admin.register(CustomSymptomSuggestion)
class CustomSymptomSuggestionAdmin(admin.ModelAdmin):
    list_display = ['symptom_name', 'is_approved', 'suggested_by', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['symptom_name', 'suggested_by__user__username']
    readonly_fields = ['created_at']
    actions = ['approve_suggestions']
    
    def approve_suggestions(self, request, queryset):
        """Admin action to approve symptom suggestions and add them to Symptom model"""
        count = 0
        for suggestion in queryset:
            if not suggestion.is_approved:
                # Create the actual symptom in the Symptom model
                Symptom.objects.get_or_create(
                    name=suggestion.symptom_name,
                    defaults={'description': suggestion.symptom_description}
                )
                suggestion.is_approved = True
                suggestion.save()
                count += 1
        self.message_user(request, f'{count} symptom(s) approved and added to the database.')
    
    approve_suggestions.short_description = 'Approve selected suggestions and add to symptoms'
