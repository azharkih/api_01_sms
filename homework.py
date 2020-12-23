import logging
import os
import time
from json import JSONDecodeError
from typing import Union

import requests
from dotenv import load_dotenv
from twilio.rest import Client

logging.basicConfig(level=logging.DEBUG, filename='sms.log',
                    format='%(asctime)s %(name)s %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

load_dotenv()
NUMBER_FROM = os.getenv('NUMBER_FROM')
NUMBER_TO = os.getenv('NUMBER_TO')
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

VK_ACCESS_TOKEN = os.getenv('VK_ACCESS_TOKEN')
VK_API_VERSION = '5.92'

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def _get_base_user_info(user_id: Union[str, int]) -> dict:
    """
    Вернуть информацию о пользователе ВКонтакте.

    user_id: Union[str, int]
        перечисленные через запятую идентификаторы пользователей или их короткие
        имена.
    """
    data = {
        'v': VK_API_VERSION,
        'access_token': VK_ACCESS_TOKEN,
        'user_ids': user_id,
        'fields': 'online'
    }
    try:
        user_info = requests.post('https://api.vk.com/method/users.get',
                                  params=data).json().get('response')[0]
    except JSONDecodeError:
        logger.error('Сервис не доступен')
        print('Сервис не доступен')
        exit()
    except TypeError:
        logger.error('Ошибочный запрос')
        print('Ошибочный запрос')
        exit()
    return user_info


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
    message = client.messages.create(
        body=sms_text,
        from_=NUMBER_FROM,
        to=NUMBER_TO
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
