# Generated by Django 4.2.16 on 2024-11-17 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_studentlog_logout_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentlearninglog',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
