# Generated by Django 4.2.7 on 2023-12-04 19:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('security', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.PositiveIntegerField()),
                ('year', models.PositiveIntegerField()),
                ('invoice_provider', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='invoice_provider', to='security.provider')),
                ('invoice_venue', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='invoice_venue', to='security.venue')),
                ('shifts', models.ManyToManyField(blank=True, related_name='shifts', to='security.shift')),
            ],
        ),
    ]