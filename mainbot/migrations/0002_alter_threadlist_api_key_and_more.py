# Generated by Django 4.2 on 2023-04-21 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainbot', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='threadlist',
            name='api_key',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='threadlist',
            name='crypto_remain',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='threadlist',
            name='marketing_symbol',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='threadlist',
            name='password',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='threadlist',
            name='secret_key',
            field=models.CharField(max_length=200),
        ),
    ]