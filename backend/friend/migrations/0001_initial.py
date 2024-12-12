# Generated by Django 5.1.4 on 2024-12-12 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Friendship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user1', models.BigIntegerField()),
                ('user2', models.BigIntegerField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('blocked', 'Blocked')], default='pending', max_length=10)),
                ('last_action_by', models.BigIntegerField()),
            ],
        ),
    ]
