# Generated by Django 5.1.2 on 2024-11-24 22:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutorials', '0005_merge_20241124_0011'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='frequency',
            field=models.CharField(choices=[('Weekly', 'Weekly'), ('By Weekly', 'By Weekly')], default='Weekly', max_length=20),
        ),
    ]
