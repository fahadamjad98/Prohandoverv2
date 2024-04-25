# Generated by Django 4.2.9 on 2024-04-22 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0010_delete_document'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
                ('document', models.FileField(upload_to='documents/')),
            ],
        ),
    ]
