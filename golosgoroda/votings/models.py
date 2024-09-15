from django.db import models


class Object(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название',
    )
    image = models.ImageField(
        upload_to='objects/',
        verbose_name='Изображение'
    )
    info = models.TextField(
        verbose_name='Информация'
    )
    status = models.CharField(
        choices=['active', 'deleted'],
        default='active'
    )

    class Meta:
        verbose_name = 'Объект'
        verbose_name_plural = 'Объекты'

    def __str__(self):
        return self.name


class Voting(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название'
    )
    date = models.DateField(
        auto_now_add=True,
        verbose_name='Дата',
    )

    class Meta:
        verbose_name = 'Голосование'
        verbose_name_plural = 'Голосования'

    def __str__(self):
        return self.name


class ObjectVoting(models.Model):
    object = models.OneToOneField(
        Object,
        on_delete=models.CASCADE,
        primary_key=True
    )
    voting = models.OneToOneField(
        Voting,
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = ('object', 'voting')
