# Generated by Django 3.0.4 on 2020-05-20 09:51

from django.db import migrations, models


def set_is_pinned_default(apps, schema_editor):
    News = apps.get_model('news', 'news')
    News.objects.update(is_pinned=False)


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0009_auto_20200519_0617'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='is_pinned',
            field=models.NullBooleanField(default=False),
        ),
        migrations.RunPython(set_is_pinned_default),
        migrations.AlterField(
            model_name='news',
            name='is_pinned',
            field=models.BooleanField(default=False),
        ),
    ]
