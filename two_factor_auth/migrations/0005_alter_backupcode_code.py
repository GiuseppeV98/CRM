# Generated by Django 5.0.3 on 2024-03-20 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('two_factor_auth', '0004_backupcode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backupcode',
            name='code',
            field=models.CharField(max_length=128),
        ),
    ]
