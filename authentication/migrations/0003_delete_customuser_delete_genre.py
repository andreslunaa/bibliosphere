# Generated by Django 4.2.6 on 2023-10-31 17:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_customuser_selected_genres_alter_customuser_groups_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CustomUser',
        ),
        migrations.DeleteModel(
            name='Genre',
        ),
    ]