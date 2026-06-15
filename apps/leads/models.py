from django.db import models
from django.utils import timezone
from solo.models import SingletonModel


class Lead(models.Model):
    class Type(models.TextChoices):
        CALLBACK = 'callback', 'Обратный звонок'
        ORDER = 'order', 'Заказ'

    class Status(models.TextChoices):
        NEW = 'new', 'Новая'
        PROCESSED = 'processed', 'Обработана'

    name = models.CharField(max_length=200, verbose_name='Имя')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    email = models.EmailField(blank=True, verbose_name='Email')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.ORDER, verbose_name='Тип')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW, verbose_name='Статус')
    consent = models.BooleanField(verbose_name='Согласие на обработку персональных данных')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    product = models.ForeignKey(
        'catalog.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Товар',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
    
    def __str__(self):
        return f'{self.name} — {self.get_type_display()} ({self.created_at:%d.%m.%Y})'
    
    def as_message(self) -> str:
        lines = [
            f'Новая заявка: {self.get_type_display()}',
            f'Имя: {self.name}',
            f'Телефон: {self.phone}',
        ]
        if self.email:
            lines.append(f'Email: {self.email}')
        if self.product:
            lines.append(f'Товар: {self.product}')
        if self.comment:
            lines.append(f'Комментарий: {self.comment}')
        lines.append(f'Дата: {timezone.localtime(self.created_at):%d.%m.%Y %H:%M}')
        return '\n'.join(lines)


class AmoCRMAuth(SingletonModel):
    access_token = models.TextField('Access token', blank=True)
    refresh_token = models.TextField('Refresh token', blank=True)
    expires_at = models.DateTimeField('Истекает', null=True, blank=True)

    class Meta:
        verbose_name = 'amoCRM — авторизация'
        verbose_name_plural = 'amoCRM — авторизация'

    def __str__(self):
        return 'amoCRM — авторизация'
