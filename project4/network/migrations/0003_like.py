# Generated by Django 4.1.7 on 2023-03-09 17:57

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0002_post_follow'),
    ]

    operations = [
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('liker', models.ManyToManyField(related_name='all_likes', to=settings.AUTH_USER_MODEL)),
                ('post', models.ManyToManyField(related_name='all_likes', to='network.post')),
            ],
        ),
    ]
