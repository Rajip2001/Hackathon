<<<<<<< HEAD
=======
# Generated by Django 4.2.16 on 2024-09-21 01:36
>>>>>>> c11a5fa123fae12dd44a2533bb6c5887906342a5

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0002_rename_id_skillset_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='skillset',
            old_name='user',
            new_name='id',
        ),
    ]
