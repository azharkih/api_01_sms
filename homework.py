import os
import time
from typing import Union

import requests
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()


def _get_base_user_info(user_id: Union[str, int]) -> dict:
    """
    Вернуть информацию о пользователе ВКонтакте.

    user_id: Union[str, int]
        перечисленные через запятую идентификаторы пользователей или их короткие
        имена.
    """
    data = {
        'v': '5.92',
        'access_token': os.getenv('VK_ACCESS_TOKEN'),
        'user_ids': user_id,
        'fields': 'online'
    }
    user_info = requests.post('https://api.vk.com/method/users.get',
                              params=data)
    return user_info.json().get('response')[0]


def get_status(user_id: Union[str, int]) -> str:
    """
    Вернуть статус нахождения пользователя в сети.

    user_id: Union[str, int]
        перечисленные через запятую идентификаторы пользователей или их короткие
        имена.
    """
    return _get_base_user_info(user_id).get('online')


def get_user_vk_full_name(user_id: Union[str, int]) -> str:
    """
    Вернуть полное имя пользователя.

    user_id: Union[str, int]
        перечисленные через запятую идентификаторы пользователей или их короткие
        имена.
    """
    user_info = _get_base_user_info(user_id)
    return ' '.join([user_info.get('first_name'), user_info.get('last_name')])


def sms_sender(sms_text: str) -> str:
    """
    Отправить сообщение и вернуть SID отправленного сообщения.

    sms_text: str
        Текст сообщения.
    """
    client = Client(os.getenv('TWILIO_ACCOUNT_SID'),
                    os.getenv('TWILIO_AUTH_TOKEN'))

    message = client.messages.create(
        body=sms_text,
        from_=os.getenv('NUMBER_FROM'),
        to=os.getenv('NUMBER_TO')
    )
    return message.sid


if __name__ == '__main__':
    vk_id = input('Введите id ')
    vk_name = get_user_vk_full_name(vk_id)
    while True:
        if get_status(vk_id) == 1:
            sms_sender(f'{vk_name} сейчас онлайн!')
            break
        time.sleep(5)
