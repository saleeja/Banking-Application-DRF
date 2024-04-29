# Generated by Django 5.0.4 on 2024-04-29 21:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0006_account_transaction_limit'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='transactions_made',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
