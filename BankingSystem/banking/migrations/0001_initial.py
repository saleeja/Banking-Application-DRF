# Generated by Django 5.0.4 on 2024-04-29 15:25

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_type', models.CharField(choices=[('savings', 'Savings'), ('current', 'Current'), ('fixed_deposit', 'Fixed Deposit'), ('recurring_deposit', 'Recurring Deposit')], max_length=20)),
                ('account_number', models.CharField(blank=True, max_length=12, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CurrentAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('business_name', models.CharField(max_length=255)),
                ('nature_of_business', models.CharField(max_length=255)),
                ('business_address', models.TextField()),
                ('business_phone_number', models.CharField(max_length=20)),
                ('business_email_address', models.EmailField(max_length=254)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='banking.account')),
            ],
        ),
        migrations.CreateModel(
            name='FixedDepositAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duration_months', models.PositiveIntegerField()),
                ('deposit_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('source_account_id', models.PositiveIntegerField()),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fixed_deposit_account', to='banking.account')),
            ],
        ),
        migrations.CreateModel(
            name='RecurringDepositAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monthly_deposit_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('duration_months', models.PositiveIntegerField()),
                ('source_account_id', models.PositiveIntegerField()),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recurring_deposit_account', to='banking.account')),
            ],
        ),
        migrations.CreateModel(
            name='SavingAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Purpose', models.CharField(max_length=255)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='banking.account')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('transaction_date', models.DateTimeField(auto_now_add=True)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('status', models.CharField(max_length=20)),
                ('fee_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_transactions', to='banking.account')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_transactions', to='banking.account')),
            ],
        ),
    ]
