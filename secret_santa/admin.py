from django.contrib import admin
from django.utils.html import format_html
from secret_santa.models import User, MailList
from django import forms

class MailListInline(admin.TabularInline):
    model = MailList.members.through
    verbose_name = "Рассылки пользователя"
    verbose_name_plural = "Рассылки пользователя"


class UserAdmin(admin.ModelAdmin):
    actions = ['mailing', 'regenerate', 'reset']
    list_display = ['name', 'giver_to']
    inlines = [
        MailListInline,
    ]

    def mailing(self, request, queryset):
        mailing_users(queryset)
        self.message_user(request, "Создана рассылка для выбранных пользователей")

    def reset(self, request, queryset):
        User.objects.all().update(has_giver=False, gifts_to=None, giver_to=None)
        self.message_user(request, "Распределение участников сброшено")


    def regenerate(self, request, queryset):
        assign_givers()
        self.message_user(request, "Участники распределены")

    mailing.short_description = "Создать рассылку"
    regenerate.short_description = "Распределить участников"
    reset.short_description = "Сбросить распределение"


class MailListForm(forms.ModelForm):
    message = forms.CharField(
        widget=forms.Textarea,
        label='Текст'
    )
    class Meta:
        model = MailList
        fields = '__all__'


class MailListAdmin(admin.ModelAdmin):
    actions = ['send']
    form = MailListForm
    filter_horizontal = ['members']
    list_display = ['name', 'members_number', 
                    'is_scheduled', 'send_mail']
    
    def is_scheduled(self, obj):
        return obj.scheduled_time if obj.is_scheduled else '-'

    def send_mail(self, obj):
        return format_html(
            '<a href="/admin/maillist/{0}/send" class="button">Отправить</a>&nbsp;',
            obj.id
        )
    
    def members_number(self, obj):
        return obj.members.count()
    
    def send(self, request, queryset):
        self.message_user(request, "Рассылка отправлена")

    send.short_description = "Отправить рассылку"
    send_mail.short_description = "Действия"
    send_mail.allow_tags = True
    is_scheduled.short_description = "Запланирована"
    members_number.short_description = "Получателей"


admin.site.register(User, UserAdmin)
admin.site.register(MailList, MailListAdmin)


from django.db.models import (Case, ExpressionWrapper, F, IntegerField, Sum,
                              Value, When)
from django.db.models.functions import Abs
from django.db.models.functions.comparison import Coalesce
from django.http import HttpResponse

from secret_santa.models import User


def assign_givers():
    users = User.objects.filter(giver_to=None)
    user_ids = list(users.values_list("id", flat=True))
    for id in user_ids:
        user = users.get(id=id)
        free_users = User.objects.exclude(id=user.id)\
                .exclude(has_giver=True)\
                .annotate(
            priority=ExpressionWrapper(
                Sum(
                    Case(
                        When(room=user.room, then=Value(0)),
                        default=Value(10),
                        output_field=IntegerField(),
                    ) +
                    Coalesce(Abs(F('year') - user.year), 0),
                    output_field=IntegerField(),
                ),
                output_field=IntegerField(),
            )).order_by("-priority")
        if not free_users:
            fix_last_one()
            break
        selected_user = free_users.first()

        user.gifts_to = selected_user.id
        user.giver_to = selected_user

        user.current_priority = selected_user.priority
        user.save()
        selected_user.has_giver = True
        selected_user.save()

    return HttpResponse()


def fix_last_one():
    loner = User.objects.get(giver_to=None, has_giver=False)
    other = User.objects.exclude(id=loner.id).order_by("current_priority").first()
    if other:
        loner.gifts_to = other.gifts_to
        loner.giver_to = other.giver_to

        other.gifts_to = loner.id
        other.giver_to = loner

        loner.has_giver = True
        other.save()
        loner.save()


def delete_user(id):
    user = User.objects.get(id=id)
    giver = User.objects.get(gifts_to=id)
    receiver = User.objects.get(id=user.gifts_to)
    print(giver, receiver)
    User.objects.filter(id=receiver.id).update(has_giver=False)
    User.objects.filter(id=giver.id).update(giver_to=None)
    user.delete()
    assign_givers()


def mailing_users(queryset):
    maillist = MailList.objects.create(
        name= "Новая рассылка"
    )
    maillist.members.set(queryset)
    maillist.save()