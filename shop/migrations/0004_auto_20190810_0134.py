# Generated by Django 2.2.3 on 2019-08-09 22:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_auto_20190810_0132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='label',
            field=models.CharField(choices=[('P', 'NEW'), ('S', 'SALE'), ('D', 'DISCOUNT')], max_length=1),
        ),
    ]
