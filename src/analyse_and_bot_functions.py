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
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
import pylab as pltt
import datetime
import matplotlib.dates as mdates




token = "65e6efa565e6efa565e6efa54f6593fb1f665e665e6efa53a5c6937a4636b3416a8bd92"
group_token = "17e681fbe171945431a04f1abc752d41ff888698288abf74124de4e782c67f36e76484601991870f56b7a"
new_token = "812c2975fc2ac0785252d97e8b5011f45e873a00dfb98b15299aec060ff7b890d06c4822feab0626e198c"
our_group_id = 200698416

analyse_group_id = 'memkn'
my_group_id = 'memkn_funclub'
my_number_group_id = 200698416
album_id = 278041850
version = '5.95'

session1 = vk.AuthSession(access_token=token)
session2 = vk.AuthSession(access_token=group_token)
vk_api = vk.API(session1, v=5.92)
vk_api2 = vk.API(session2, v=5.92)

month_length = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
days_of_the_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
days_of_the_week2 = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}


def upload_picture(picture_path):
    """
    uploading a picture to an album in vk group
    :param picture_path:
    :return an answer of request:
    """
    r = vk_api.photos.getUploadServer(group_id=our_group_id, album_id=album_id)
    url = r['upload_url']
    file = {'file1': open(picture_path, 'rb')}
    ur = requests.post(url, files=file).json()
    result = requests.get('https://api.vk.com/method/photos.save',
                          params={
                              'access_token': new_token,
                              'album_id': ur['aid'],
                              'group_id': ur['gid'],
                              'server': ur['server'],
                              'photos_list': ur['photos_list'],
                              'hash': ur['hash'],
                              'v': version,
                          }).json()
    return url


def get_message(group_id, server_, ts_, key_):
    # gets the message from the user
    response = requests.get('{server}?act=a_check&key={key}&ts={ts}&wait=25'.format
                            (server=server_, key=key_, ts=ts_)).json()
    if 'updates' in response and len(response['updates']) > 0:
        return response['updates'][0]['object']['body'], response['updates'][0]['object']['user_id'], response['ts']
    return "", -1, response['ts']


def process_input_message(message):
    # gets the massage from the user and returns a code which depends on the message type. Also returns the group id
    # and needed frequency. These fields will be used afterwards only if the message is: group_id: ...; period: ...
    """
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
    :param message: the message that was sent by the user
    :return: special code, string - the group id or "" - and a number - the period of analysing or -1
    """
    if message == "":
        return 0, "", -1
    if message[:2] == "gr" and message[2] == ':' and message[3:].strip() in days_of_the_week2:
        return 13, "", days_of_the_week2[message[3:].strip()]
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


def get_new_random_id():
    t = datetime.datetime.now()
    random_id = t.minute * 60000 + t.second * 1000 + t.microsecond
    return random_id


def switch_off(current_user_id, begin_file_):
    # switches the bot off, the special password is needed
    r_id = get_new_random_id()
    file_ = open(begin_file_, "w")
    file_.write(f"-1 0 0 0")
    file_.close()
    vk_api2.messages.send(user_id=current_user_id, message="Goodbye!", random_id=r_id)
    return


def incorrect_id(current_user_id):
    # informs about the mistake
    r_id = get_new_random_id()
    vk_api2.messages.send(user_id=current_user_id, message="Wrong group id!", random_id=r_id)
    return


def incorrect_period_value(current_user_id):
    # informs about the mistake
    r_id = get_new_random_id()
    s = "Period should be not less than 15 and should divide 1440!"
    vk_api2.messages.send(user_id=current_user_id, message=s, random_id=r_id)
    return


def cancel_the_task(have_a_task, current_user_id, master_id, begin_file_):
    # Cancels the current task, it is is asked by the user who gave the task earlier
    r_id = get_new_random_id()
    file_ = open(begin_file_, "w")
    file_.write(f"-1 0 0 0")
    file_.close()
    if have_a_task and current_user_id == master_id:
        vk_api2.messages.send(user_id=current_user_id, message="Your task is cancelled!", random_id=r_id)
        return
    elif have_a_task:
        vk_api2.messages.send(user_id=current_user_id, message="Sorry, I am working on the other user's task!",
                              random_id=r_id)
        return
    else:
        vk_api2.messages.send(user_id=current_user_id, message="Я сделал ничего, не благодари!",
                              random_id=r_id)
        return


def say_hello(current_user_id):
    # sends a message 'Ну привет, ....'
    r_id = get_new_random_id()
    string = "Ну привет, "
    value = vk_api2.users.get(user_ids=current_user_id, fields='first_name')
    string += value[0]['first_name']
    something = vk_api2.messages.send(user_id=current_user_id, message=string, random_id=r_id)
    return


def instruction_message(current_user_id):
    # sends the message if user did send us the message of an unknown format
    r_id = get_new_random_id()
    string = "Maaaaaaan! I don't understand you... Read the instruction please. If you need it in a bigger variant"
    string += ", send 'help'"

    vk_api2.messages.send(
        user_id=current_user_id, message=string, attachment="photo-200698416_457239022", random_id=r_id
    )
    return


def check_recommend_time(time_string):
    if time_string[3] != ':' or not time_string[1: 3].isdigit() or not time_string[4: 6].isdigit():
        return 0
    hours = int(time_string[1: 3])
    if 0 <= hours < 24:
        return 1
    return 0


def set_time(current_user_id):
    r_id = get_new_random_id()

    kb = \
        {
            "inline": True,
            "buttons": [
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
                ],
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


def check_for_correct(group_id_to_check):
    your_group_info = vk_api2.groups.getById(group_id=group_id_to_check, fields='members_count', count=5)
    if your_group_info[0]['id'] == my_number_group_id and group_id_to_check != 'memkn_funclub':
        return 0
    return 1


def check_period_for_correct(period):
    if period < 15 or period > 1440:
        return 0
    if period < 60 and 60 % period != 0:
        return 0
    if 1440 % period != 0:
        return 0
    return 1


def not_available(current_user_id):
    r_id = get_new_random_id()
    vk_api2.messages.send(user_id=current_user_id, message="Not available now!", random_id=r_id)
    vk_api2.messages.send(user_id=current_user_id, sticker_id=4331, random_id=(r_id + 1))
    return


# dicts belong -- samples of dicts for functions


def time_from_db_to_date(time_string):
    """
    time in table is string, so this formatting it to a timedate. example:
    time_string = "Mon, 10:30"
                   0123456789
    :param time_string:
    :return timedate:
    """

    moment_hours = int(time_string[5])*10 + int(time_string[6])
    moment_minutes = int(time_string[8])*10 + int(time_string[9])
    moment_days = 7
    if time_string[:3] == "Mon":
        moment_days = 1
    if time_string[:3] == "Tue":
        moment_days = 2
    if time_string[:3] == "Wed":
        moment_days = 3
    if time_string[:3] == "Thu":
        moment_days = 4
    if time_string[:3] == "Fri":
        moment_days = 5
    if time_string[:3] == "Sat":
        moment_days = 6
    auxiliary_delta = datetime.timedelta(days=moment_days, hours=moment_hours, minutes=moment_minutes)
    # time from the beginning of the week
    abstract_sunday = datetime.datetime(2020, 12, 27)
    final_time = abstract_sunday + auxiliary_delta
    return final_time


def dict_with_strings_to_dict_for_plots(dict_with_strings):
    """
    converting result of request to db to dict for plot funstions
    :param dict_with_strings:
    :return:
    """
    new_dict = {}
    for key in dict_with_strings:
        key_for_new_dict = time_from_db_to_date(key)
        new_dict[key_for_new_dict] = dict_with_strings[key]
    return new_dict


def create_daily_image(dict_with_data, label_of_image):
    """
    an image for daily report
    :param dict_with_data:
    :param label_of_image:
    :return nothing:
    """
    day_delta = 0
    prev_key = datetime.datetime.now()
    for key in dict_with_data:
        day_delta = key - prev_key
        prev_key = key
    period = day_delta.total_seconds()
    period = period // 60
    number_of_dots = int(1440 // period)
    y_axis = [0] * int(number_of_dots)
    x_axis = [datetime.datetime(2020, 1, 1, 0, 0, 0) + day_delta * i for i in range(number_of_dots)]
    for key in dict_with_data:
        y_axis[int((key.minute + key.hour * 60) // period)] = dict_with_data[key]
    # belong is decoration for graph
    figure, ax = plt.subplots(figsize=(number_of_dots, 10))
    ax.set_title(label_of_image)
    ax.set_xlabel("Время", fontsize=14)
    ax.set_ylabel("Процент онлайна", fontsize=14)
    ax.grid(which="major", linewidth=1.2)
    ax.grid(which="minor", linestyle="--", color="gray", linewidth=0.5)
    ax.scatter(x_axis, y_axis, c="red")
    ax.plot(x_axis, y_axis)
    my_fmt = mdates.DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(my_fmt)
    figure.savefig("../data/images/" + label_of_image + ".png")
    return


def task_by_button(current_user_id):
    r_id = get_new_random_id()
    vk_api2.messages.send(
        user_id=current_user_id,
        message="Send the group_id and the period with a whitespace between them and '$' in the beginning",
        random_id=r_id
    )