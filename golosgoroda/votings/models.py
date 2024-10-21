from django.contrib.auth import get_user_model
from django.db import models
from minio_storage.storage import MinioMediaStorage

User = get_user_model()


class Object(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активный'),
        ('deleted', 'Удален'),
    ]
    ms = MinioMediaStorage()

    name = models.CharField(max_length=255, verbose_name='Название объекта')
    description = models.TextField(verbose_name='Описание')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES,
                              default='active', verbose_name='Статус')
    image = models.ImageField(storage=ms, verbose_name='Изображение')

    class Meta:
        verbose_name = 'Объект'
        verbose_name_plural = 'Объекты'

    def __str__(self):
        return self.name


class Voting(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('deleted', 'Удален'),
        ('formed', 'Сформирован'),
        ('completed', 'Завершен'),
        ('rejected', 'Отклонен'),
    ]

    title = models.CharField(
        max_length=255,
        null=True,
        verbose_name='Название голосования'
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES,
        default='draft', verbose_name='Статус'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    formed_at = models.DateTimeField(
        verbose_name='Дата формирования',
        null=True, blank=True
    )
    completed_at = models.DateTimeField(
        verbose_name='Дата завершения',
        null=True, blank=True
    )
    voting_date = models.DateTimeField(
        verbose_name='Дата голосования',
        null=True,
    )
    total_votes = models.IntegerField(default=0)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='votings', verbose_name='Создатель'
    )
    moderator = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        blank=True, related_name='moderated_votings',
        verbose_name='Модератор'
    )

    class Meta:
        verbose_name = 'Голосование'
        verbose_name_plural = 'Голосования'

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, '-')

    def __str__(self):
        return f'Голосование {self.title} - {self.status}'


class VotingObject(models.Model):
    voting = models.ForeignKey(
        Voting, on_delete=models.CASCADE,
        verbose_name='Голосование'
    )
    object = models.ForeignKey(
        Object, on_delete=models.CASCADE,
        verbose_name='Объект'
    )
    votes_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество голосов'
    )

    class Meta:
        managed = True
        db_table = 'votings_votingobject'
        constraints = [
            models.UniqueConstraint(fields=['voting', 'object'],
                                    name='unique_voting_object')
        ]
        verbose_name = 'Связь голосования и объекта'
        verbose_name_plural = 'Связи голосований и объектов'

    def __str__(self):
        return f'{self.object.name} в голосовании {self.voting.title}'
