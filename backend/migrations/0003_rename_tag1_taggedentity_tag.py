# Generated by Django 4.0.2 on 2022-02-14 14:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0002_rename_tag_taggedentity_tag1'),
    ]

    operations = [
        migrations.RenameField(
            model_name='taggedentity',
            old_name='tag1',
            new_name='tag',
        ),
    ]
