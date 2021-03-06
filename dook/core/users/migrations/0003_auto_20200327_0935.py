# Generated by Django 3.0.4 on 2020-03-27 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20200326_1645'),
    ]

    operations = [
        migrations.AddField(
            model_name='invitation',
            name='user_role',
            field=models.CharField(choices=[('fact_checker', 'Fact Checker'), ('expert', 'Expert')], default='fact_checker', max_length=30),
        ),
        migrations.AlterField(
            model_name='invitation',
            name='sent_at',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_verified',
            field=models.BooleanField(default=True),
        ),
    ]
