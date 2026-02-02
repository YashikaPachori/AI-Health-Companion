# Generated manually for disease_name and predicted_disease blank

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prediction', '0002_customsymptomsuggestion'),
    ]

    operations = [
        migrations.AddField(
            model_name='predictionhistory',
            name='disease_name',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='predictionhistory',
            name='predicted_disease',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, to='prediction.disease'),
        ),
    ]
