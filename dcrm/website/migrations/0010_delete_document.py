# Generated by Django 4.2.9 on 2024-04-22 11:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0009_remove_document_description_remove_document_document_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Document',
        ),
    ]