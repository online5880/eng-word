# Generated by Django 4.2.16 on 2024-11-15 05:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_studentinfo_grade'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentlog',
            name='logout_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]