# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='affinity',
            old_name='brand_id',
            new_name='brand',
        ),
        migrations.RenameField(
            model_name='affinity',
            old_name='profile_id',
            new_name='profile',
        ),
    ]
