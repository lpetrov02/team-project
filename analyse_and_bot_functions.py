import vk
import datetime
import requests
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


def get_user_last_seen(profile_id):
    """
    shows when user was online
    :param profile_id:
    :return time:
    """
    value = vk_api.users.get(user_ids=profile_id, fields='last_seen')
    if 'last_seen' not in value[0]:
        return None
    online_time = datetime.datetime.fromtimestamp(value[0]['last_seen']['time'])
    return online_time


def get_group_followers(group_page_id, done):
    """
    gets the list of the group members, not more than 1000
    :param group_page_id:
    :param done: shows the indent
    :return list of members' ids:
    """
    value = vk_api.groups.getMembers(group_id=group_page_id, offset=done)
    followers_id = []
    for user in value['items']:
        followers_id.append(user)
    return followers_id


def approximate_time(real_time):
    """
    gets time user was last seen and adds two minutes
    :param real_time: time user was last seen online
    :return: real_time plus delta min
    """

    hours = real_time.hour
    days = real_time.day
    months = real_time.month
    years = real_time.year
    # обработка редких случаев
    if years % 4 == 0 and years % 100 != 0 or years % 400 == 0:
        month_length[1] += 1
    if real_time.minute >= 58:
        hours = real_time.hour + 1
    if hours == 24:
        hours = 0
        days += 1
    if days > month_length[months - 1]:
        days = 1
        months += 1
    if months > 12:
        months = 1
        years += 1

    approximate_online_time = real_time.replace(minute=(real_time.minute + 2) % 60,
                                                hour=hours, day=days, month=months, year=years)
    return approximate_online_time


def is_online(online_time):
    # just checks if the user is online or not, returns 0 or 1

    now_time = datetime.datetime.now()
    now_time = now_time.replace(microsecond=0)
    if online_time >= now_time:
        return 1
    else:
        return 0


def get_message(group_id, server_, ts_, key_):
    # gets the message from the user
    response = requests.get('{server}?act=a_check&key={key}&ts={ts}&wait=25'.format
                            (server=server_, key=key_, ts=ts_)).json()
    if len(response['updates']) > 0:
        return response['updates'][0]['object']['body'], response['updates'][0]['object']['user_id'], response['ts']
    return "", -1, response['ts']


def count_new_time(time_now, period):
    # gets the time, when the counting stats process was last started and returns time, when to start the process again.
    # just adds period.
    d_minutes = period
    d_hours = 0
    if period > 59:
        d_minutes = period % 60
        d_hours = period // 60
    minutes = time_now.minute
    hours = time_now.hour
    days = time_now.day
    months = time_now.month
    years = time_now.year
    if years % 4 == 0 and years % 100 != 0 or years % 400 == 0:
        month_length[1] += 1

    minutes = (minutes + d_minutes) % 60
    if minutes < time_now.minute:
        hours += 1
    hours += d_hours
    if hours > 23:
        hours %= 24
        days += 1
    if days > month_length[time_now.month - 1]:
        days = 1
        months += 1
    if months > 12:
        months = 1
        years += 1
    month_length[1] -= 1

    new_time = time_now.replace(minute=minutes, hour=hours, day=days, month=months, year=years)
    return new_time


def process_input_message(message):
    # gets the massage from the user and returns a code which depends on the message type. Also returns the group id
    # and needed frequency. These fields will be used afterwards only if the message is: group_id: ...; period: ...
    if message == "stop" or message == "Stop":
        return 1, "", -1
    if message == "":
        return 0, "", -1
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
        elif int(period) < 60 and 60 % int(period) != 0 or int(period) < 15 or 1440 % int(period) != 0:
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
    return -1, "", -1


def get_r_id(current_user_id):
    obj = vk_api2.messages.getHistory(user_id=current_user_id, offset=0, extended=1)
    if len(obj['items']) == 0:
        return 1
    else:
        for i in range(20):
            if obj['items'][i]['from_id'] == -my_number_group_id:
                return obj['items'][i]['random_id'] + 1


def switch_off(current_user_id):
    # switches the bot off, the special password is needed
    r_id = get_r_id(current_user_id)
    vk_api2.messages.send(user_id=current_user_id, message="Goodbye!", random_id=r_id)
    return 0


def incorrect_id(current_user_id):
    # informs about the mistake
    r_id = get_r_id(current_user_id)
    vk_api2.messages.send(user_id=current_user_id, message="Wrong group id!", random_id=r_id)
    return


def incorrect_period_value(current_user_id):
    # informs about the mistake
    r_id = get_r_id(current_user_id)
    s = "Period should be not less than 15 and should divide 1440!"
    vk_api2.messages.send(user_id=current_user_id, message=s, random_id=r_id)
    return


def cancel_the_task(have_a_task, current_user_id, master_id):
    # Cancels the current task, it is is asked by the user who gave the task earlier
    r_id = get_r_id(current_user_id)
    if have_a_task and current_user_id == master_id:
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
    r_id = get_r_id(current_user_id)
    string = "Ну привет, "
    value = vk_api2.users.get(user_ids=current_user_id, fields='first_name')
    string += value[0]['first_name']
    something = vk_api2.messages.send(user_id=current_user_id, message=string, random_id=r_id)
    return


def instruction_message(current_user_id):
    # sends the message if user did send us the message of an unknown format
    r_id = get_r_id(current_user_id)
    string = "Maaaaaaan! I don't understand you...   "
    string += "You can SAY HELLO: your message should start with 'hello' or 'привет';   "
    string += "You can GIVE ME A TASK in such a way: 'group_id: 'the_group_id'; period: 'period'.   "
    string += "Period should be pretty and not too small)   "
    string += "You can CANCEL YOUR TASK: just send 'stop'   "
    string += "Have a good day!!"
    # vk_api2.messages.send(user_id=current_user_id, sticker_id=8616, random_id=count)
    vk_api2.messages.send(user_id=current_user_id, message=string, attachment="photo-200698416_457239021",
                          random_id=r_id)
    return


def check_for_correct(group_id):
    try:
        your_group_info = vk_api.groups.getById(group_id=group_id, fields='members_count', count=1)
    except vk.exceptions.VkAPIError:
        return 0
    return 1


def not_available(current_user_id):
    r_id = get_r_id(current_user_id)
    vk_api2.messages.send(user_id=current_user_id, message="Not available now!", random_id=r_id)
    vk_api2.messages.send(user_id=current_user_id, sticker_id=4331, random_id=(r_id + 1))
    return