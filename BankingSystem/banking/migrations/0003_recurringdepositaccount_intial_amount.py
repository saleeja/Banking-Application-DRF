# Generated by Django 5.0.4 on 2024-04-29 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0002_alter_fixeddepositaccount_deposit_amount_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='recurringdepositaccount',
            name='intial_amount',
            field=models.DecimalField(decimal_places=2, default=2, max_digits=10),
            preserve_default=False,
        ),
    ]