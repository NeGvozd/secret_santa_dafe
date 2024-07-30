from django.http import HttpResponse, HttpResponseRedirect
from secret_santa.models import User, MailList
from secret_santa.admin import assign_givers
from secret_santa.bot import send_message
import json


def delete_user(request):
    id = request.POST["id"]
    try:
        user = User.objects.get(vk_id=id)
    except User.DoesNotExist:
        user = User.objects.get(telegram_id=id)

    giver_to_user = User.objects.get(gifts_to=id)
    receiver_from_user = User.objects.get(id=user.gifts_to)
    # print(giver_to_user, receiver_from_user)

    User.objects.filter(id=receiver_from_user.id).update(has_giver=False)
    User.objects.filter(id=giver_to_user.id).update(gifts_to=None)

    user.delete()
    assign_givers()
    return HttpResponse(200)


def add_user(request):
    data = json.loads(request.POST)
    User.objects.create(
            id=data.get("id"),
            telegram_id=data.get("telegram_id"),
            vk_id=data.get("vk_id"),
            name=data.get("name"),
            wishes=data.get("wishes"),
            room=data.get("room", None),
            year=data.get("year", None),
            has_giver=False,
            current_priority=0
    )
    return HttpResponse(200)


def send_mail(request, maillist_id):
    mail = MailList.objects.get(id=maillist_id)
    send_message(mail.members.all(), mail.message, mail.image)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])