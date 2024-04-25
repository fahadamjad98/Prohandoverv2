# Generated by Django 4.2.9 on 2024-04-22 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0008_remove_document_owner_remove_document_property_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='description',
        ),
        migrations.RemoveField(
            model_name='document',
            name='document',
        ),
        migrations.RemoveField(
            model_name='document',
            name='uploaded_at',
        ),
        migrations.AddField(
            model_name='document',
            name='docfile',
            field=models.FileField(default=1, upload_to='documents/%Y/%m/%d'),
            preserve_default=False,
        ),
    ]
