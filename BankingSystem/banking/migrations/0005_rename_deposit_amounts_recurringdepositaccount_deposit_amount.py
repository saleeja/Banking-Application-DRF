# Generated by Django 5.0.4 on 2024-04-29 20:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0004_rename_monthly_deposit_amount_recurringdepositaccount_deposit_amounts'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recurringdepositaccount',
            old_name='deposit_amounts',
            new_name='deposit_amount',
        ),
    ]