"""
Management command to sync symptoms from the ML model's DISEASE_SYMPTOM_MAP
into the Symptom table so the check-symptoms page shows all symptoms used for prediction.
Run: python manage.py sync_symptoms
"""
from django.core.management.base import BaseCommand

from prediction.models import Symptom
from prediction.ml_model import DiseasePredictionModel


def normalized_to_display(name):
    """Convert normalized symptom (e.g. chest_pain) to display name (e.g. Chest pain)."""
    return name.replace('_', ' ').strip().title()


class Command(BaseCommand):
    help = 'Sync symptoms from ML model DISEASE_SYMPTOM_MAP into the Symptom table.'

    def handle(self, *args, **options):
        all_symptoms = set()
        for disease_symptoms in DiseasePredictionModel.DISEASE_SYMPTOM_MAP.values():
            all_symptoms.update(disease_symptoms)
        created = 0
        for norm_name in sorted(all_symptoms):
            display_name = normalized_to_display(norm_name)
            if not Symptom.objects.filter(name__iexact=display_name).exists():
                Symptom.objects.create(name=display_name, description='')
                created += 1
        self.stdout.write(self.style.SUCCESS(f'Synced symptoms: {len(all_symptoms)} total, {created} new.'))
