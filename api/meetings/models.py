from django.db import models
from api.oauth.models import User
# Create your models here.


class RoomImage(models.Model):
    """ Образ комнаты """

    name = models.CharField('Название', max_length=150)
    description = models.JSONField('Описание')
    preview_image = models.ImageField('Preview', upload_to='uploads/previews/')

    class Meta:
        verbose_name = 'Образ комнаты'
        verbose_name_plural = 'Образы комнаты'

    def __str__(self):
        return self.name


class Room(models.Model):
    """ Комната """

    name = models.CharField(max_length=150)
    room_image = models.ForeignKey(RoomImage, models.CASCADE, verbose_name='Образ комнаты')

    # config
    can_customers_speak = models.BooleanField('Могут ли клиенты говорить', default=True)

    slug = models.SlugField(max_length=150, unique=True)

    class Meta:
        verbose_name = 'Комната'
        verbose_name_plural = 'Комнаты'

    def __str__(self):
        return self.room_image.name


class Meeting(models.Model):
    """ Встреча """

    name = models.CharField('Название', max_length=150)
    owners = models.ManyToManyField(User, verbose_name='Создатель', related_name='owners')
    customers = models.ManyToManyField(User, verbose_name='Посетители', related_name='customers', blank=True)
    black_list = models.ManyToManyField(User, verbose_name='Чёрный список', related_name='black_list', blank=True)
    password = models.CharField('Ключ доступа', max_length=150, null=True, default=None)
    rooms = models.ManyToManyField(Room, verbose_name='Комнаты')
    slug = models.SlugField(max_length=150, unique=True)

    class Meta:
        verbose_name = 'Встреча'
        verbose_name_plural = 'Встречи'

    def __str__(self):
        return self.name
