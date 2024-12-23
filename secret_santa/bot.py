import vk_api, os, time
from vk_api.longpoll import VkLongPoll, VkEventType
from django.core.management import BaseCommand
from .models import User
from secret_santa.secrets import VK_TOKEN

token = VK_TOKEN
vk_session = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()

def value_validation(field, value):
        if field == 'year' and (value < 1 or value > 6):
            raise ValueError
        if field == 'room' and (value < 1 or value > 167):
            raise ValueError


class Command(BaseCommand):
    help = 'Запуск бота'

    def handle(self, *args, **options):
        while True:
            try:
                self.run_bot()
            except Exception as e:
                vk.messages.send(user_id='162745048', message="Ошибка подключения, попытка перезапуска", random_id=0)
                time.sleep(5)
        

    def run_bot(self):
        longpoll = VkLongPoll(vk_session)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                self.handle_message(event)


    def handle_message(self, event):
        user_id = event.user_id

        if User.objects.filter(vk_id=user_id).exists():
            return

        text = event.text.strip()

        steps = [
            ("Привет! Для участия в Тайном Санте пройди, пожалуйста, небольшую регистрацию:\nнапиши свои имя и фамилию", 'start'),
            ("Теперь номер курса (цифрой)", 'name'),
            ("Номер комнаты в общежитии (чтобы мы знали, куда в случае чего передать подарок)", 'year'),
            ("Пожелания к подарку (рекомендую писать как можно конкретнее)", 'room'),
            ("Проверяем данные...", 'wishes'),
        ]

        if user_id not in user_data:
            user_data[user_id] = {'step': 0, 'data': {}}

        current_step = user_data[user_id]['step']        
        # print(user_id, current_step, event.text)

        if current_step < len(steps):
            message, field = steps[current_step]

            if field == 'year' or field == 'room':
                try:
                    value = int(text)
                    value_validation(field, value)
                    user_data[user_id]['data'][field] = value
                except ValueError:
                    vk.messages.send(user_id=user_id, message="Введи корректное число)\nНомера курсов: 1-6 (если аспирантура или выпускник - пиши 6 :))\nЕсли не живешь в общежитии ФАЛТа, то пиши комнату человека, через которого можно передать подарок", random_id=0)
                    return
            
            elif current_step > 0:
                user_data[user_id]['data'][field] = text

            vk.messages.send(user_id=user_id, message=message, random_id=0)
            current_step += 1
            user_data[user_id]['step'] = current_step

        if current_step >= len(steps):
            data = user_data[user_id]['data']
            User.objects.create(
                vk_id=user_id,
                name=data['name'],
                year=data['year'],
                room=data['room'],
                wishes=data['wishes'],
            )
            vk.messages.send(user_id=user_id, message="Регистрация завершена!) Осталось дождаться рассылки с человеком, кому будешь дарить подарок)", random_id=0)
            del user_data[user_id]


user_data = {}


def send_message(users_set, message, image=None):
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()

    users_set = users_set.select_related('giver_to').values(
        'vk_id',
        'giver_to__name',
        'giver_to__year',
        'giver_to__wishes',
    )

    for user in users_set:
        if image:
            upload = vk_api.VkUpload(vk_session)
            photo = upload.photo_messages(photos=image.path)[0]
            attachemt = f'photo{photo["owner_id"]}_{photo["id"]}'
            vk.messages.send(user_id=user['vk_id'], message=message, attachment=attachemt, random_id=0)
        else:
            # рассылка с данными людей приходит только без картинок. Код очень плохой, надо переписать 
            try:
                personalized_message = message.format(user['giver_to__name'], user['giver_to__year'], user['giver_to__wishes'])
            except KeyError:
                personalized_message = message
                
            vk.messages.send(user_id=user['vk_id'], message=personalized_message, random_id=0)
    