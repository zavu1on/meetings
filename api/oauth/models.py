from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import models
# Create your models here.


def validate_size_image(file):
    megabyte_limit = 2

    if file.size > megabyte_limit * 1024 * 1024:
        raise ValidationError(f'Максимальный размер файла {megabyte_limit}MB')


class User(AbstractUser):
    """ Пользователь """

    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    email = models.EmailField(_('email address'), unique=True)
    patronymic = models.CharField('Отчество', max_length=150, blank=True, null=True)
    avatar = models.ImageField(
        'Аватар',
        default='anon.jpg',
        validators=[validate_size_image],
        upload_to='uploads/avatars/'
    )

    def get_full_name(self):
        return f'{self.last_name} {self.first_name} {self.patronymic}'


class Token(models.Model):
    """ Access токены пользователей """

    token = models.TextField('JWT токен')
    user = models.ForeignKey(User, models.CASCADE)

    def __str__(self):
        return self.token

    class Meta:
        verbose_name = 'Токен'
        verbose_name_plural = 'Токены'


class RegistrationUserData(models.Model):
    """ Данные пользователя для регистрации """

    username = models.CharField('Логин', max_length=150, unique=True)
    email = models.EmailField('Email', unique=True)
    password = models.CharField('Пароль', max_length=150)
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    patronymic = models.CharField('Отчество', max_length=150)
    uuid = models.UUIDField(null=True, blank=True)

    def __str__(self):
        return self.uuid.__str__()

    class Meta:
        verbose_name = verbose_name_plural = 'Данные пользователя для регистрации'


class RecoverUserPasswordData(models.Model):
    """ Данные пользователя для восстановления пароля """

    username = models.CharField('Логин', max_length=150)
    email = models.EmailField('Email')
    uuid = models.UUIDField(null=True, blank=True)
    user = models.ForeignKey(User, models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.uuid.__str__()

    class Meta:
        verbose_name = verbose_name_plural = 'Данные пользователя для восстановления пароля'
