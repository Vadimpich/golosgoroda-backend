# Generated by Django 5.1.1 on 2024-09-23 05:50

import django.db.models.deletion
import minio_storage.storage
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Object',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название объекта')),
                ('description', models.TextField(verbose_name='Описание')),
                ('status', models.CharField(choices=[('active', 'Активный'), ('deleted', 'Удален')], default='active', max_length=10, verbose_name='Статус')),
                ('image', models.ImageField(storage=minio_storage.storage.MinioMediaStorage(), upload_to='', verbose_name='Изображение')),
                ('address', models.CharField(max_length=255, verbose_name='Адрес объекта')),
            ],
            options={
                'verbose_name': 'Объект',
                'verbose_name_plural': 'Объекты',
            },
        ),
        migrations.CreateModel(
            name='Voting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Название голосования')),
                ('status', models.CharField(choices=[('draft', 'Черновик'), ('deleted', 'Удален'), ('formed', 'Сформирован'), ('completed', 'Завершен'), ('rejected', 'Отклонен')], default='draft', max_length=10, verbose_name='Статус')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('formed_at', models.DateTimeField(verbose_name='Дата формирования')),
                ('completed_at', models.DateTimeField(verbose_name='Дата завершения')),
                ('voting_date', models.DateTimeField(blank=True, null=True, verbose_name='Дата проведения')),
                ('moderator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='moderated_votings', to=settings.AUTH_USER_MODEL, verbose_name='Модератор')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votings', to=settings.AUTH_USER_MODEL, verbose_name='Создатель')),
            ],
            options={
                'verbose_name': 'Голосование',
                'verbose_name_plural': 'Голосования',
            },
        ),
        migrations.CreateModel(
            name='VotingObject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('votes_count', models.PositiveIntegerField(default=0, verbose_name='Количество голосов')),
                ('object', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='votings.object', verbose_name='Объект')),
                ('voting', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='votings.voting', verbose_name='Голосование')),
            ],
            options={
                'verbose_name': 'Связь голосования и объекта',
                'verbose_name_plural': 'Связи голосований и объектов',
                'db_table': 'votings_votingobject',
                'managed': True,
            },
        ),
    ]