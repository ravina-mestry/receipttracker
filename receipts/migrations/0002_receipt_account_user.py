# Generated by Django 2.1 on 2021-11-30 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('receipts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='receipt',
            name='account_user',
            field=models.IntegerField(default=2, verbose_name='Account User'),
        ),
    ]
