import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chores', '0002_chore'),
    ]

    operations = [
        migrations.AddField(
            model_name='chore',
            name='created_at',
            # auto_now_add populates new rows; existing rows are backfilled with
            # the migration-time timestamp so the schema change can't fail on
            # pre-existing data. preserve_default=False keeps the default off the
            # model state (auto_now_add handles inserts from here on).
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
