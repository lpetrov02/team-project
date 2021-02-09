import vk
import datetime
import requests
import json
# from new_main import vk_api2 as vk_api2
# from new_main import month_length as month_length
import group_class as gc
import time
import random
import math


token = "65e6efa565e6efa565e6efa54f6593fb1f665e665e6efa53a5c6937a4636b3416a8bd92"
group_token = "17e681fbe171945431a04f1abc752d41ff888698288abf74124de4e782c67f36e76484601991870f56b7a"
analyse_group_id = 'memkn'
my_group_id = 'memkn_funclub'
my_number_group_id = 200698416

session1 = vk.AuthSession(access_token=token)
session2 = vk.AuthSession(access_token=group_token)
vk_api = vk.API(session1, v=5.92)
vk_api2 = vk.API(session2, v=5.92)

month_length = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
days_of_the_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def get_message(group_id, server_, ts_, key_):
    # gets the message from the user
    response = requests.get('{server}?act=a_check&key={key}&ts={ts}&wait=25'.format
                            (server=server_, key=key_, ts=ts_)).json()
    if 'updates' in response and len(response['updates']) > 0:
        return response['updates'][0]['object']['body'], response['updates'][0]['object']['user_id'], response['ts']
    return "", -1, response['ts']


def find_the_task(group_id, user_id, tasks):
    for x in range(len(tasks)):
        if tasks[x]['master'] == user_id and tasks[x]['group'].group_id == group_id:
            return x
    return -1


def find_the_group(group_id, tasks):
    for x in tasks:
        if x['group'].group_id == group_id:
            return 1
    return 0


def process_input_message(message):
    # gets the massage from the user and returns a code which depends on the message type. Also returns the group id
    # and needed frequency. These fields will be used afterwards only if the message is: group_id: ...; period: ...
    if message == "":
        return 0, ""
    if message[0] == '~':
        if not check_recommend_time(message):
            return -1, ""
        if len(message) < 7 or not check_for_correct(message[6:].strip()):
            return 5, ""
        return 12, message
    if message == "Начать":
        return 14, ""
    if message == "Что обрабатывается для меня?":
        return 15, ""
    if message == "Сколько свободных мест?":
        return 13, ""
    if message == "Текущий процент: ВКЛ":
        return 17, "1"
    if message == "Текущий процент: ВЫКЛ":
        return 17, "0"
    if message == "Set time":
        return 11, ""
    if message == "Want to give a task":
        return 10, ""
    if message.lower() == "help":
        return 9, ""
    if len(message) > 4 and (message[0: 4] == "stop" or message[0: 4] == "Stop") and message[4] == ':':
        group_to_stop = message[5:].strip()
        if not check_for_correct(group_to_stop):
            return 5, group_to_stop
        return 1, group_to_stop
    if message == "lsr_memkn6":
        return 2, ""
    string1 = message[0: 6]
    string2 = message[0: 5]
    if string1 == "Привет" or string1 == "привет" or string2 == "Hello" or string2 == "hello":
        return 4, ""
    if len(message) > 13 and (message[0: 13] == "Recommend day" or
                              message[0: 13] == "recommend day") and message[13] == ':':
        recommend_group = message[14:].strip()
        if not check_for_correct(recommend_group):
            return 5, recommend_group
        return 7, recommend_group
    if len(message) > 14 and (message[0: 14] == "Recommend week" or
                              message[0: 14] == "recommend week") and message[14] == ':':
        recommend_group = message[15:].strip()
        if not check_for_correct(recommend_group):
            return 5, recommend_group
        return 8, recommend_group
    if message[0] == '$' and " " not in message[1:].strip():
        group = message[1:].strip()
        if not check_for_correct(group):
            return 5, ""
        if not check_group_size(group):
            return 16, ""
        return 3, group
    return -1, ""


def get_r_id():
    t = datetime.datetime.now()
    random_id = t.minute * 60000000 + t.second * 1000000 + t.microsecond
    return random_id


def switch_off(current_user_id, tasks):
    # switches the bot off, the special password is needed
    r_id = get_r_id()
    vk_api2.messages.send(user_id=current_user_id, message="Я терпел, но сегодня я ухожу...", random_id=r_id)
    value = vk_api2.users.get(user_ids=current_user_id, fields=['first_name', 'last_name'])
    string = f"потому что меня выключил {value[0]['last_name']} {value[0]['first_name']}"
    for x in tasks:
        r_id = get_r_id()
        vk_api2.messages.send(
            user_id=x['master'],
            message=f"Ваш запрос по группе '{x['group'].name}' отменён, {string}",
            random_id=r_id)
    return 0


def incorrect_id(current_user_id):
    # informs about the mistake
    r_id = get_r_id()
    vk_api2.messages.send(user_id=current_user_id, message="Группы с таким айдишником нету как бэ", random_id=r_id)
    return


def cancel_the_task(have_a_task, index_to_delete, current_user_id):
    # Cancels the current task, it is is asked by the user who gave the task earlier
    r_id = get_r_id()
    have_a_task.pop(index_to_delete)
    vk_api2.messages.send(user_id=current_user_id, message="Штош, отменяю!",
                          random_id=r_id)
    return


def say_hello(current_user_id):
    # sends a message 'Ну привет, ....'
    r_id = get_r_id()
    string = "Ну привет, "
    value = vk_api2.users.get(user_ids=current_user_id, fields='first_name')
    string += value[0]['first_name']
    something = vk_api2.messages.send(user_id=current_user_id, message=string, random_id=r_id)
    return


def instruction_message(current_user_id):
    # sends the message if user did send us the message of an unknown format
    r_id = get_r_id()
    string = "Я вас не понимаю! Пожалуйста, прочитайте инструкцию! "
    string += "Получить инструкцию можно, нажав на кнопочку 'help'"

    # attachment="photo-200698416_457239022"
    vk_api2.messages.send(
        user_id=current_user_id, message=string, random_id=r_id
    )
    return


def check_recommend_time(time_string):
    if time_string[3] != ':' or not time_string[1: 3].isdigit() or not time_string[4: 6].isdigit():
        return 0
    hours = int(time_string[1: 3])
    if 0 <= hours < 24:
        return 1
    return 0


def send_big_instruction(current_user_id):
    # sends the instruction for the user
    r_id = get_r_id()

    kb = \
    {
        "one_time": False,
        "buttons": [
            [
                {
                    "action": {
                        "type": "text",
                        "payload": "{\"button\": \"2\"}",
                        "label": "help"
                    },
                    "color": "positive"
                },
                {
                    "action": {
                        "type": "text",
                        "payload": "{\"button\": \"2\"}",
                        "label": "Сколько свободных мест?"
                    },
                    "color": "primary"
                }
            ],
            [
                {
                    "action": {
                        "type": "text",
                        "payload": "{\"button\": \"2\"}",
                        "label": "Что обрабатывается для меня?"
                    },
                    "color": "secondary"
                }
            ],
            [
                {
                    "action": {
                        "type": "text",
                        "payload": "{\"button\": \"2\"}",
                        "label": "Текущий процент: ВКЛ"
                    },
                    "color": "positive"
                },
                {
                    "action": {
                        "type": "text",
                        "payload": "{\"button\": \"2\"}",
                        "label": "Текущий процент: ВЫКЛ"
                    },
                    "color": "negative"
                }
            ]
        ]
    }

    kb = json.dumps(kb, ensure_ascii=False).encode('utf-8')
    kb = str(kb.decode('utf-8'))

    text = "Вот что я понимаю и умею:\n 1) $group_id - где вместо group_id айдишник нужной группы. " + \
           "Я приму группу на обаботку и буду писылать отчёты. \n\n" + \
           "2) recommend day: group_id - именно в таком фомате. Я пришлю лучшее время для постов за сегодня\n\n" + \
           "3) recommend week: group_id - именно в таком фомате." + \
           "Я пришлю лучшее время для постов за текущую неделю\n\n" + \
           "4) ~22:00 group_id - тут минуты значения не имеют, можно всегда писать 00, а вместо 22 - любое число" + \
           ", не большее 23, конечно. Тогда отчёты по группе group_id будут приходить в указанный час\n\n" + \
           "5) Stop: group_id - и я сразу перестану следить за группой group_id\n\n" + \
           "Можно здооваться - 'привет' или 'hello' а начале предложения\n\n"

    vk_api2.messages.send(
        user_id=current_user_id,
        message=text,
        # attachment="photo-200698416_457239023",
        random_id=r_id,
        keyboard=kb
    )
    return


def send_keyboard(current_user_id):
    # sends the instruction for the user
    r_id = get_r_id()

    kb = \
    {
        "one_time": False,
        "buttons": [
            [
                {
                    "action": {
                        "type": "text",
                        "payload": "{\"button\": \"2\"}",
                        "label": "help"
                    },
                    "color": "positive"
                },
                {
                    "action": {
                        "type": "text",
                        "payload": "{\"button\": \"2\"}",
                        "label": "Сколько свободных мест?"
                    },
                    "color": "primary"
                }
            ],
            [
                {
                    "action": {
                        "type": "text",
                        "payload": "{\"button\": \"2\"}",
                        "label": "Что обрабатывается для меня?"
                    },
                    "color": "secondary"
                }
            ],
            [
                {
                    "action": {
                        "type": "text",
                        "payload": "{\"button\": \"2\"}",
                        "label": "Текущий процент: ВКЛ"
                    },
                    "color": "positive"
                },
                {
                    "action": {
                        "type": "text",
                        "payload": "{\"button\": \"2\"}",
                        "label": "Текущий процент: ВЫКЛ"
                    },
                    "color": "negative"
                }
            ]
        ]
    }

    kb = json.dumps(kb, ensure_ascii=False).encode('utf-8')
    kb = str(kb.decode('utf-8'))

    vk_api2.messages.send(
        user_id=current_user_id,
        message="Лови клавиатуру)",
        random_id=r_id,
        keyboard=kb
    )
    return


def check_for_correct(group_id_to_check):
    your_group_info = vk_api2.groups.getById(group_id=group_id_to_check, fields='members_count', count=5)
    if your_group_info[0]['id'] == my_number_group_id and group_id_to_check != 'memkn_funclub':
        return 0
    return 1


def not_available(current_user_id):
    r_id = get_r_id()
    vk_api2.messages.send(user_id=current_user_id, message="Временно недоступно!", random_id=r_id)
    vk_api2.messages.send(user_id=current_user_id, sticker_id=4331, random_id=(r_id + 1))
    return


def cannot_receive_more_tasks(current_user_id):
    r_id = get_r_id()
    vk_api2.messages.send(user_id=current_user_id, message="Извини, я уже завален работой...", random_id=r_id)
    vk_api2.messages.send(user_id=current_user_id, sticker_id=2, random_id=(r_id + 1))
    return


def have_such_a_task_already(current_user_id):
    r_id = get_r_id()
    vk_api2.messages.send(user_id=current_user_id, message="Чел, ты... уже давал мне такое задание...", random_id=r_id)
    vk_api2.messages.send(user_id=current_user_id, sticker_id=6158, random_id=(r_id + 1))
    return


def no_such_a_task(current_user_id):
    r_id = get_r_id()
    vk_api2.messages.send(
        user_id=current_user_id, message="Вы мне такой группы на обработку не давали...", random_id=r_id
    )
    vk_api2.messages.send(user_id=current_user_id, sticker_id=6559, random_id=(r_id + 1))
    return


def free_places(current_user_id, number):
    r_id = get_r_id()
    number = 10 - number
    if number > 4:
        vk_api2.messages.send(
            user_id=current_user_id, message=f"Могу принять ещё {number} запросов", random_id=r_id
        )
    elif number == 1:
        vk_api2.messages.send(
            user_id=current_user_id, message="Могу принять ещё один запрос", random_id=r_id
        )
    elif 1 < number < 5:
        vk_api2.messages.send(
            user_id=current_user_id, message=f"Могу принять {number} запроса", random_id=r_id
        )
    else:
        vk_api2.messages.send(
            user_id=current_user_id, message="Мне жаль, но я загужен до отказа((", random_id=r_id
        )
    return


def task_by_button(current_user_id):
    r_id = get_r_id()
    vk_api2.messages.send(
        user_id=current_user_id,
        message="Send the group_id and the period with a whitespace between them and '$' in the beginning",
        random_id=r_id
    )


def user_groups(current_user_id, have_a_task):
    r_id = get_r_id()
    found_something = 0
    groups = ""
    for x in have_a_task:
        if x['master'] == current_user_id:
            found_something = 1
            groups += x['group'].name + "\n"
    if found_something:
        vk_api2.messages.send(
            user_id=current_user_id, message=("Вот ваши группы: \n" + groups), random_id=r_id
        )
    else:
        vk_api2.messages.send(
            user_id=current_user_id, message="Вы ещё не давали заданий", random_id=r_id
        )


def check_group_size(group_id):
    your_group_info = vk_api.groups.getById(group_id=group_id, fields='members_count')
    number_of_members = your_group_info[0]['members_count']
    if number_of_members > 500000:
        return 0
    return 1


def too_big_group(current_user_id):
    r_id = get_r_id()
    vk_api2.messages.send(
        user_id=current_user_id,
        message="Ваша группа слишком большая, её обработка существенно меня затормозит, так что прошу простить",
        random_id=r_id
    )


def change_recommend_time(begin_file, task_number, return_message):
    file = open(begin_file, "r")
    commands = list(file.read().split('\n'))
    file.close()
    file = open(begin_file, "w")
    for cmd_number in range(len(commands)):
        if cmd_number != task_number:
            file.write(commands[cmd_number] + '\n')
        else:
            ind = commands[cmd_number].rfind(" ")
            file.write(commands[cmd_number][:ind] + f" {int(return_message[1: 3])}" + '\n')
    file.close()
