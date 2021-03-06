# Generated by Django 3.0.4 on 2020-03-30 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0001_initial'),
        ('users', '0003_auto_20200327_0935'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitation',
            name='email',
            field=models.EmailField(error_messages={'unique': 'Zaproszenie z takim adresem email już istnieje.'}, max_length=254, unique=True, verbose_name='e-mail address'),
        ),
        migrations.AlterUniqueTogether(
            name='usernews',
            unique_together={('news', 'user')},
        ),
    ]
