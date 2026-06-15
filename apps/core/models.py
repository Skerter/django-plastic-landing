import re

from django.db import models
from solo.models import SingletonModel


def _tel(value: str) -> str:
    digits = re.sub(r'[^\d]', '', value or '')
    return f'+{digits}' if digits else ''


class SiteSettings(SingletonModel):
    company_name = models.CharField(
        'Название компании', max_length=255, default='ООО «ДемоПласт»',
        help_text='Официальное название. Выводится в подвале, реквизитах и микроразметке.',
    )

    # --- Контакты ---
    phone_sales = models.CharField(
        'Телефон — отдел продаж', max_length=32, blank=True,
        help_text='Главный телефон. Формат как для показа: +7 495 000-00-00. '
                  'Ссылка tel: соберётся автоматически.',
    )
    phone_sales_person = models.CharField(
        'ФИО — продажи', max_length=255, blank=True,
        help_text='Контактное лицо отдела продаж. Показывается на странице «Контакты».',
    )
    email_sales = models.EmailField(
        'E-mail отдела продаж', blank=True,
        help_text='Адрес для заявок. На него приходят письма о новых заявках с сайта.',
    )
    phone_production = models.CharField(
        'Телефон — производство', max_length=32, blank=True,
        help_text='Формат как для показа: +7 495 000-00-01.',
    )
    phone_production_person = models.CharField(
        'ФИО — производство', max_length=255, blank=True,
        help_text='Контактное лицо производства.',
    )
    phone_accounting = models.CharField(
        'Телефон — бухгалтерия', max_length=32, blank=True,
        help_text='Формат как для показа: +7 495 000-00-02.',
    )
    email_accounting = models.EmailField(
        'E-mail бухгалтерии', blank=True,
        help_text='Адрес для счетов и документов. Показывается на «Контактах».',
    )

    # --- Адрес и режим ---
    address = models.CharField(
        'Адрес производства', max_length=255, blank=True,
        help_text='Например: г. Москва, ул. Промышленная, д. 1. Выводится в подвале и контактах.',
    )
    # Режим работы делится на две строки, чтобы выводить их раздельно
    # (будни — крупно в шапке/подвале, выходные — отдельной строкой на «Контактах»).
    work_hours = models.CharField(
        'Режим работы в будни', max_length=128, blank=True,
        help_text='Например: ПН–ПТ · 08:00–17:00',
    )
    work_hours_weekend = models.CharField(
        'Режим работы в выходные', max_length=128, blank=True,
        help_text='Например: СБ–ВС: выходной',
    )
    map_query = models.CharField(
        'Запрос для Яндекс.Карт', max_length=255, blank=True,
        help_text='Текст, по которому строится карта на «Контактах». '
                  'Например: Москва, улица Промышленная, 1',
    )

    # --- Реквизиты ---
    legal_address = models.CharField(
        'Юридический адрес', max_length=255, blank=True,
        help_text='С индексом. Например: 101000, г. Москва, ул. Промышленная, д. 1',
    )
    inn = models.CharField('ИНН', max_length=12, blank=True, help_text='10 или 12 цифр.')
    kpp = models.CharField('КПП', max_length=9, blank=True, help_text='9 цифр.')
    ogrn = models.CharField('ОГРН', max_length=15, blank=True, help_text='13 цифр.')
    okpo = models.CharField('ОКПО', max_length=14, blank=True)
    account = models.CharField(
        'Расчётный счёт', max_length=20, blank=True, help_text='20 цифр.',
    )
    bank = models.CharField(
        'Банк', max_length=255, blank=True, help_text='Полное название банка.',
    )
    bik = models.CharField('БИК', max_length=9, blank=True, help_text='9 цифр.')
    corr_account = models.CharField(
        'Корр. счёт', max_length=20, blank=True, help_text='20 цифр.',
    )
    
    # --- Уведомления и аналитика ---
    metrika_id = models.CharField(
        'ID счётчика Яндекс.Метрики', max_length=16, blank=True,
        help_text='Номер счётчика из кабинета Метрики (например 98765432). '
                  'Пусто — Метрика отключена. Грузится только при согласии на cookie.',
    )
    notify_email_enabled = models.BooleanField(
        'Отправлять заявки на email', default=True,
        help_text='Если включено — о новой заявке приходит письмо на адрес ниже.',
    )
    email_notifications = models.EmailField(
        'E-mail для уведомлений', blank=True,
        help_text='Адрес, на который сайт шлёт письма о новых заявках. На сайте не виден.'
                  'Не путать с e-mail продаж в «Контактах» — здесь только для уведомлений.',
    )
    notify_telegram_enabled = models.BooleanField(
        'Отправлять уведомления в Telegram', default=False,
        help_text='Требует токен бота (в .env).',
    )
    telegram_chat_id = models.CharField(
        'Telegram chat_id', max_length=64, blank=True,
        help_text='ID чата для уведомлений о заявках. На сайте не виден.',
    )
    notify_amocrm_enabled = models.BooleanField(
        'Отправлять заявки в amoCRM', default=False,
        help_text='Требует настройки интеграции amoCRM (в .env) и авторизации.',
    )



    class Meta:
        verbose_name = 'Настройки сайта'
        verbose_name_plural = 'Настройки сайта'

    def __str__(self):
        return 'Настройки сайта'

    @property
    def phone_sales_tel(self):
        return _tel(self.phone_sales)

    @property
    def phone_production_tel(self):
        return _tel(self.phone_production)

    @property
    def phone_accounting_tel(self):
        return _tel(self.phone_accounting)

