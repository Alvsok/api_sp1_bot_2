import os
import requests
import telegram
import time
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL_PRAK_YANDEX_API = 'https://praktikum.yandex.ru/api/'

'''
отключаем прокси за ненадобностью
proxy = telegram.utils.request.Request(
    proxy_url='socks5://159.89.49.60:31264')
bot = telegram.Bot(token=TELEGRAM_TOKEN, request=proxy)
'''
bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):

    statuses = {
        'approved': True,
        'rejected': False,
    }

    homework_name = homework.get('homework_name')
    homework_status = statuses.get(homework.get('status'))

    if homework_name is None or homework_status is None:
        print('Сервер вернул: ', homework)
        return 'Неверный ответ от сервера'

    if homework_status:
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    else:
        verdict = 'К сожалению в работе нашлись ошибки.'

    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    if current_timestamp is None:
        current_timestamp = time.time()
    params = {
        'from_date': current_timestamp
    }
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

    url = '{source}{query}/{method}/'.format(
        source=URL_PRAK_YANDEX_API,
        query='user_api',
        method='homework_statuses',
    )

    params['from_date'] = 0                    # вставка 1

    try:
        return requests.get(
            url,
            params=params,
            headers=headers
        ).json()
    except requests.RequestException:
        print('Ошибка подключения к серверу')
        return {}
    except ValueError:
        print('Ошибка типа данных, полученных с сервера')
        return {}


def send_message(message):
    return bot.send_message(CHAT_ID, message)


def main():
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(
                    new_homework.get('homeworks')[0]))
            current_timestamp = new_homework.get('current_date')

            # вставка 2
            target_work_name = 'api_sp1_bot'
            work_name = new_homework.get('homeworks')[0].get('homework_name')
            if target_work_name in work_name:
                time.sleep(999999)  # заснуть навсегда
            else:
                time.sleep(1000)  # опрашивать раз в 16.67 минут
            time.sleep(1000)  # опрашивать раз в 16.67 минут

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
