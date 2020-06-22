import os
import requests
import telegram
import time
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL_PRAK_YANDEX = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'


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
        verdict = 'Ревьюеру всё понравилось, '
        verdict += 'можно приступать к следующему уроку.'
    else:
        verdict = 'К сожалению в работе нашлись ошибки.'

    return f'У вас проверили работу "{homework_name}"!\n{verdict}'


def get_homework_statuses():

    params = {'from_date': 0}
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

    try:
        return requests.get(
            URL_PRAK_YANDEX,
            params=params,
            headers=headers,
        ).json()

    except requests.RequestException:
        print('Ошибка подключения к серверу')
        return {}
    except ValueError:
        print('Ошибка типа данных, полученных с сервера')
        return {}


def send_message(message):
    return bot.send_message(CHAT_ID, message)


def main(target_work_name):

    # flag = True

    while True:
        try:
            new_homework = get_homework_statuses()
            work_name = new_homework.get('homeworks')[0].get('homework_name')

            if target_work_name in work_name:
                res = parse_homework_status(new_homework.get('homeworks')[0])
                send_message(res)
                return
                # flag = Falses
                # time.sleep(99999999)
            else:
                time.sleep(1000)

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


ask = 'api_sp1_bot'
if __name__ == '__main__':
    main(ask)
