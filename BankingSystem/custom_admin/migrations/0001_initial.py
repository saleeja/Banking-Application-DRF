# Generated by Django 5.0.4 on 2024-04-29 15:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('banking', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fixed_interest_rate', models.DecimalField(decimal_places=2, max_digits=5)),
                ('recurring_interest_rate', models.DecimalField(decimal_places=2, max_digits=5)),
                ('transaction_limit', models.IntegerField(default=5)),
                ('max_transaction_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('min_deposit_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='banking.account')),
            ],
        ),
    ]
