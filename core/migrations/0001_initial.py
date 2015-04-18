# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Affinity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_mod', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_mod', models.DateTimeField(auto_now=True)),
                ('affinities', models.ManyToManyField(to='core.Brand', through='core.Affinity')),
            ],
        ),
        migrations.AddField(
            model_name='affinity',
            name='brand',
            field=models.ForeignKey(to='core.Brand'),
        ),
        migrations.AddField(
            model_name='affinity',
            name='profile',
            field=models.ForeignKey(to='core.Profile'),
        ),
        migrations.AlterUniqueTogether(
            name='affinity',
            unique_together=set([('profile', 'brand')]),
        ),
    ]
