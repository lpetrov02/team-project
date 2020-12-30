import vk
import datetime
import requests
import json
import random
# from new_main import vk_api2 as vk_api2
# from new_main import month_length as month_length
# import matplotlib
import group_class as gc
import time
import random
import math


# top-secret information
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


# THE FUNCTION WHICH REALISE INTERACTION WITH SERVER
def get_message(server_, ts_, key_):
    """
    this function gets message from a user
    :param server_:
    :param ts_: something technical
    :param key_: also something technical
    :return:
    """

    response = requests.get('{server}?act=a_check&key={key}&ts={ts}&wait=25'.format
                            (server=server_, key=key_, ts=ts_)).json()
    if 'updates' in response and len(response['updates']) > 0:
        return response['updates'][0]['object']['body'], response['updates'][0]['object']['user_id'], response['ts']
    return "", -1, response['ts']


# THE BLOCK OF FUNCTIONS WHICH PROCESS MESSAGES FROM A USER AND CHECK IF GIVEN PARAMETERS ARE CORRECT
def process_input_message(message):
    """
    gets the massage from the user and returns a code which depends on the message type. Also returns the group id
    and needed period. These fields will be used afterwards only if the message is: group_id: ...; period: ...
    :param message: the massage got from the server
    :return: special code, group id and period
    code -1: mistake
    code 0: no message
    code 1: user wants to cancel the task
    code 2: developer wants to switch the bot off
    code 3: we have received the task
    code 4: greetings
    code 5: incorrect group id
    code 6: incorrect period value
    code 7: the user asks for today's statistics
    code 8: user asks for this week's statistics
    code 9: user needs the instruction
    code 10: the user needs the advice how to give a task
    code 11: user wants to set time and has pressed the button
    code 12: user wants to set recommendation time and has entered this time already
    """

    if message == "":
        return 0, "", -1
    if message[0] == '~':
        if not check_recommend_time(message):
            return -1, "", -1
        return 12, message, -1
    if message == "Set time":
        return 11, "", -1
    if message == "Want to give a task":
        return 10, "", -1
    if message.lower() == "help":
        return 9, "", -1
    if message == "stop" or message == "Stop":
        return 1, "", -1
    if message == "lsr_memkn6":
        return 2, "", -1
    if message.count(';') == 1:
        index = message.find(';')
        if message[0: 9].strip() != "group_id:" or message[index + 1:].count('d') != 1 \
                or message[index + 1: message[index + 1:].find('d') + 3 + index].strip() != "period:":
            return -1, "", -1
        period = message[message[index + 1:].find('d') + 3 + index:].strip()
        group = message[9: index].strip()
        if not check_for_correct(group):
            return 5, "", -1
        if not period.isdigit():
            return -1, "", -1
        elif not check_period_for_correct(int(period)):
            return 6, "", -1
        else:
            return 3, group, int(period)
    string1 = message[0: 6]
    string2 = message[0: 5]
    if string1 == "Привет" or string1 == "привет" or string2 == "Hello" or string2 == "hello":
        return 4, "", -1
    if message == "Recommend: day" or message == "recommend: day":
        return 7, "", -1
    if message == "Recommend: week" or message == "recommend: week":
        return 8, "", -1
    if message[0] == '$' and message[1:].strip().count(" ") == 1:
        whitespace = message.find(' ')
        group = message[1: whitespace].strip()
        if not check_for_correct(group):
            return 5, "", -1
        period = message[whitespace + 1:].strip()
        if not period.isdigit():
            return -1, "", -1
        if not check_period_for_correct(int(period)):
            return 6, "", -1
        return 3, group, int(period)
    return -1, "", -1


def check_recommend_time(time_string):
    """
    the option 'set time' asks the user to enter the time ant this function checks if it is correct
    :param time_string: string with that time
    :return:
    """
    if time_string[3] != ':' or not time_string[1: 3].isdigit() or not time_string[4: 6].isdigit():
        return 0
    hours = int(time_string[1: 3])
    if 0 <= hours < 24:
        return 1
    return 0


def check_for_correct(group_id_to_check):
    """
    this function check if the group which the user asked to analyze, exists
    :param group_id_to_check: that group's id
    :return:
    """
    your_group_info = vk_api2.groups.getById(group_id=group_id_to_check, fields='members_count', count=5)
    if your_group_info[0]['id'] == my_number_group_id and group_id_to_check != 'memkn_funclub':
        return 0
    return 1


def check_period_for_correct(period):
    """
    checks if the period value is OK, not 17 minutes, for example. We have special rules for this
    :param period:
    :return:
    """
    if period < 15 or period > 1440:
        return 0
    if period < 60 and 60 % period != 0:
        return 0
    if 1440 % period != 0:
        return 0
    return 1


# THE BLOCK OF FUNCTIONS FOR COMMUNICATING
def get_new_random_id():
    """
    random id is a special id of the message to send this message, it has to be unique during the hour
    :return: counted random (not random!!!) id
    """
    t = datetime.datetime.now()
    random_id = t.minute * 60000000 + t.second * 1000000 + t.microsecond
    return random_id


def switch_off(current_user_id, file_name):
    """
    switches the bot off, the special password is needed
    :param current_user_id:
    :param file_name: file with the information about the current task, we need to rewrite it
    :return:
    """
    r_id = get_new_random_id()
    file = open(file_name, "w")
    file.write("-1 0 0 0")
    file.close()
    vk_api2.messages.send(user_id=current_user_id, message="Goodbye!", random_id=r_id)
    return 0


def incorrect_id(current_user_id):
    # informs about the mistake in group id
    r_id = get_new_random_id()
    vk_api2.messages.send(
        user_id=current_user_id, message="Ummmm... Something went wrong! Incorrect group id!", random_id=r_id
    )
    return


def incorrect_period_value(current_user_id):
    # informs about the mistake in a period value
    r_id = get_new_random_id()
    s = "Bro, listen here! If your period is less than an hour, in should divide 60. And anyway, it should divide 1440)"
    vk_api2.messages.send(user_id=current_user_id, message=s, random_id=r_id)
    return


def cancel_the_task(have_a_task, current_user_id, master_id, file_name):
    """
    Cancels the current task, it is is asked by the user who gave the task earlier
    :param have_a_task: 1 if bot has a task already, 0 if it hasn't
    :param current_user_id: id of the user who wants to cancel the task
    :param master_id: id of the user who had given a task
    :param file_name: file with the information about the current task, we need to change it
    :return:
    """
    r_id = get_new_random_id()
    if have_a_task and current_user_id == master_id:
        file = open(file_name, "w")
        file.write("-1 0 0 0")
        file.close()
        vk_api2.messages.send(user_id=current_user_id, message="Your task is cancelled!", random_id=r_id)
        return 0
    elif have_a_task:
        vk_api2.messages.send(user_id=current_user_id, message="Sorry, I am working on the other user's task!",
                              random_id=r_id)
        return 1
    else:
        vk_api2.messages.send(user_id=current_user_id, message="Я сделал ничего, не благодари!",
                              random_id=r_id)
        return 0


def say_hello(current_user_id):
    # sends a message 'Ну привет, ....'
    r_id = get_new_random_id()
    greetings = [
        "Ну привет, ", "Здарова бандит-", "Hi, bro ", "Здрасьте. Кто тут лох? Ага - ", "Приветики, ты просто космос, "
    ]
    index = random.randint(0, 4)
    string = greetings[index]
    value = vk_api2.users.get(user_ids=current_user_id, fields='first_name')
    string += value[0]['first_name']
    vk_api2.messages.send(user_id=current_user_id, message=string, random_id=r_id)
    return


def send_last_upload(current_user_id):
    """
    in development
    :param current_user_id:
    :return:
    """
    r_id = get_new_random_id()
    some = vk_api.photos.get(owner_id=-200698416, album_id='278041850', rev=1, count=1)
    ph_id = some['items'][0]['id']
    string = "photo-200698416_" + str(ph_id)
    vk_api2.messages.send(user_id=current_user_id, attachment=string, random_id=r_id + 1)


def instruction_message(current_user_id):
    # sends the message if user did send us the message of an unknown format
    r_id = get_new_random_id()
    string = "Maaaaaaan! I don't understand you... Read the instruction please. If you need it in a bigger variant"
    string += ", send 'help'"

    vk_api2.messages.send(
        user_id=current_user_id, message=string, attachment="photo-200698416_457239022", random_id=r_id
    )
    return


def set_time(current_user_id):
    """
    sends the keyboard with some variants of time when to send recommendations
    :param current_user_id: id of the user who wants to set time
    :return:
    """
    r_id = get_new_random_id()

    kb = \
        {
            "inline": True,
            "buttons": [
                [
                    {
                        "action": {
                            "type": "text",
                            "payload": "{\"button\": \"1\"}",
                            "label": "~22:00"
                        },
                        "color": "primary"
                    },
                    {
                        "action": {
                            "type": "text",
                            "payload": "{\"button\": \"2\"}",
                            "label": "~23:00"
                        },
                        "color": "positive"
                    },
                    {
                        "action": {
                            "type": "text",
                            "payload": "{\"button\": \"2\"}",
                            "label": "~00:00"
                        },
                        "color": "primary"
                    }
                ],
                [
                    {
                        "action": {
                            "type": "text",
                            "payload": "{\"button\": \"2\"}",
                            "label": "~19:00"
                        },
                        "color": "positive"
                    },
                    {
                        "action": {
                            "type": "text",
                            "payload": "{\"button\": \"2\"}",
                            "label": "~20:00"
                        },
                        "color": "primary"
                    },
                    {
                        "action": {
                            "type": "text",
                            "payload": "{\"button\": \"2\"}",
                            "label": "~21:00"
                        },
                        "color": "positive"
                    }
                ]
            ]
        }

    kb = json.dumps(kb, ensure_ascii=False).encode('utf-8')
    kb = str(kb.decode('utf-8'))

    vk_api2.messages.send(
        user_id=current_user_id,
        message="When would you like to receive recommendations?",
        random_id=r_id,
        keyboard=kb
    )
    return


def send_big_instruction(current_user_id):
    # sends the instruction for the user
    r_id = get_new_random_id()

    kb = \
    {
        "one_time": False,
        "buttons": [
            [
                {
                    "action": {
                        "type": "text",
                        "payload": "{\"button\": \"1\"}",
                        "label": "Stop"
                    },
                    "color": "negative"
                },
                {
                    "action": {
                        "type": "text",
                        "payload": "{\"button\": \"2\"}",
                        "label": "help"
                    },
                    "color": "primary"
                }
            ],
            [
                {
                    "action": {
                        "type": "text",
                        "payload": "{\"button\": \"2\"}",
                        "label": "recommend: day"
                    },
                    "color": "secondary"
                },
                {
                    "action": {
                        "type": "text",
                        "payload": "{\"button\": \"2\"}",
                        "label": "recommend: week"
                    },
                    "color": "secondary"
                }
            ],
            [
                {
                    "action": {
                          "type": "text",
                          "payload": "{\"button\": \"2\"}",
                          "label": "Want to give a task"
                    },
                    "color": "positive"
                },
                {
                    "action": {
                        "type": "text",
                        "payload": "{\"button\": \"2\"}",
                        "label": "Set time"
                    },
                    "color": "primary"
                }
            ]
        ]
    }

    kb = json.dumps(kb, ensure_ascii=False).encode('utf-8')
    kb = str(kb.decode('utf-8'))

    vk_api2.messages.send(
        user_id=current_user_id,
        message="В рамочку и на стену",
        attachment="photo-200698416_457239023",
        random_id=r_id,
        keyboard=kb
    )
    return


def not_available(current_user_id):
    r_id = get_new_random_id()
    vk_api2.messages.send(user_id=current_user_id, message="Not available now, give a task at first!", random_id=r_id)
    vk_api2.messages.send(user_id=current_user_id, sticker_id=4331, random_id=(r_id + 1))
    return


def not_available_i_am_busy(current_user_id):
    r_id = get_new_random_id()
    vk_api2.messages.send(user_id=current_user_id, message="Impossible because... i am busy!", random_id=r_id)
    vk_api2.messages.send(user_id=current_user_id, sticker_id=4331, random_id=(r_id + 1))
    return


def task_by_button(current_user_id):
    # gives the instruction how to give a task
    r_id = get_new_random_id()
    vk_api2.messages.send(
        user_id=current_user_id,
        message="Send the id of the group and the period with a whitespace between them and the '$' in the beginning",
        random_id=r_id
    )


def continue_the_old_task(file_name):
    file = open(file_name, "r")
    task_from_the_previous_session = list(file.readline().split())
    gr_id = -1
    have_a_task = 0
    usr_id = -1
    prd = 0
    rec_hr = -1
    if len(task_from_the_previous_session) > 0 and task_from_the_previous_session[0] != '-1':
        gr_id = task_from_the_previous_session[0]
        usr_id = int(task_from_the_previous_session[1])
        prd = int(task_from_the_previous_session[2])
        rec_hr = int(task_from_the_previous_session[3])
        have_a_task = 1
    return gr_id, prd, usr_id, rec_hr, have_a_task
    file.close()
