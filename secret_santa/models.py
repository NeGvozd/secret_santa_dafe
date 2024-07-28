from django.db import models
from django.utils import timezone


class User(models.Model):
    id = models.AutoField(primary_key=True)
    telegram_id = models.PositiveIntegerField(
        unique=True, 
        blank=True, 
        null=True,
        verbose_name= 'Telegram ID'
    )
    vk_id = models.PositiveIntegerField(
        unique=True, 
        blank=True, 
        null=True,
        verbose_name= 'VK ID'
    )
    name = models.CharField(
        max_length=50,
        verbose_name= 'Участник'   
    )
    wishes = models.CharField(
        max_length=300,
        verbose_name= 'Желания'    
    )
    room = models.PositiveIntegerField(
        null=True, 
        blank=True,
        verbose_name= 'Комната'    
    )
    year = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name= 'Курс'    
    )
    gifts_to = models.IntegerField(
        null=True,
        unique=True,
        blank=True,
        verbose_name= 'Дарит(кому)'    
    )
    giver_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name= 'Дарит(кому)'
    )
    has_giver = models.BooleanField(default=False)
    current_priority = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name}" # {('--> ' + str(self.giver_to.name)) if self.giver_to else ''}"
    
    class Meta:
        verbose_name = 'Участник'
        verbose_name_plural = 'Участники'
    

class MailList(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name='Название'
    )
    message = models.CharField(
        max_length=1000,
        verbose_name='Текст'
    )
    image = models.ImageField(
        upload_to='images/',
        blank=True,
        verbose_name='Изображение'
    )
    members = models.ManyToManyField(
        User,
        verbose_name='Участники'
    )
    scheduled_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Дата публикации'
    )

    def schedule_is_correct(self):
        # Ensures that the scheduled time is in the future
        if self.scheduled_time and self.scheduled_time <= timezone.now():
            raise ValueError('Время рассылки не может быть раньше текущего времени')

    def __str__(self):
        return self.name
    
    def is_scheduled(self):
        return self.scheduled_time and self.scheduled_time > timezone.now()

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'