import vk
import datetime
import requests
import time
import random
import math


class Group:
    """
    we don't really need this now but i suppose it would be useful in the nearest future
    """

    def __init__(self, group_id, freq):
        self.group_id = group_id
        self.begin = datetime.datetime.now()
        self.frequency = freq

    def count_online_proportion(self):
        """
        gets the number of members online, ant the total number of members, not counting those,
        whose info is not is not available
        :param self: the object of the class Group. We need the group id
        :return: two integers - the number of members with available online-information and the number of members online
        """
        amount = 0
        online = 0
        your_group_info = vk_api.groups.getById(group_id=self.group_id, fields='members_count')
        number_of_members = your_group_info[0]['members_count']
        one_more_number_of_members = number_of_members
        already_count = 0
        while already_count < number_of_members:
            group_members_ids = vk_api.groups.getMembers(group_id=self.group_id, offset=already_count, fields='online')
            for x in group_members_ids['items']:
                if 'online' in x:
                    online += x['online']
                else:
                    one_more_number_of_members -= 1
            already_count += 1000
        if one_more_number_of_members == 0:
            return -1, -1
        else:
            return one_more_number_of_members, online

    def group_analyse(self):
        t0 = time.time()
        current_time = datetime.datetime.now()

        all_members, online_members = self.count_online_proportion()
        percent = online_members / all_members * 100
        percent = math.ceil(percent)

        t0 = time.time() - t0
        return t0, percent

    def group_analyse1(self):
        t0 = time.time()
        all_members, online_members = self.count_online_proportion()
        percent = online_members / all_members * 100
        percent = math.ceil(percent)

        t0 = time.time() - t0
        if t0 >= self.frequency * 60:
            print("Sorry, I can't work so fast, so I will count statistics as fast as i can")
            while True:
                # message, user_id = get_message(my_number_group_id)
                current_time = datetime.datetime.now()

                all_members, online_members = self.count_online_proportion()
                percent = online_members / all_members * 100
                percent = math.ceil(percent)

                print("Time: " + str(current_time) + ". Online percent in " + self.group_id + " is " + str(
                    percent) + "%")
                print(
                    "_____________________________________________________________________________________________")
        else:
            while True:
                current_time = datetime.datetime.now()
                t0 = time.time()

                all_members, online_members = self.count_online_proportion()
                percent = online_members / all_members * 100
                percent = math.ceil(percent)

                print("Time: " + str(current_time) + ". Online percent in " + self.group_id + " is " + str(
                    percent) + "%")
                print(
                    "_____________________________________________________________________________________________")
                t0 = time.time() - t0
                time.sleep(self.frequency * 60 - t0)


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
    :return: real_time plus 2 min
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
    # some = vk_api2.groups.getLongPollServer(group_id=group_id)
    response = requests.get('{server}?act=a_check&key={key}&ts={ts}&wait=25'.format
                            (server=server_, key=key_, ts=ts_)).json()
    # print(response)
    if len(response['updates']) > 0:
        return response['updates'][0]['object']['body'], response['updates'][0]['object']['user_id'], response['ts']
    return "", -1, response['ts']


some = vk_api2.groups.getLongPollServer(group_id=my_number_group_id)
current_ts = some['ts']
server = some['server']
key = some['key']
message = ""
run = 1
count = 0
while run:
    message, current_user_id, current_ts = get_message(my_number_group_id, server, current_ts, key)

    # print(message)
    if message.count(';') > 0:
        index = message.find(";")
        if message[0: 10] == "group_id: " and message[index + 2: index + 10] == "period: ":
            analyse_group_id = message[10: index]
            frequency = message[index + 10:]
            if frequency == "frequently":
                frequency_number = 0
            elif frequency.isdigit():
                frequency_number = int(frequency)
            else:
                print("Error")
                exit()

            group = Group(analyse_group_id, frequency_number)
            start_time, percent = group.group_analyse()
            string = "Online percent in " + group.group_id + " is " + str(percent) + "%"
            vk_api2.messages.send(user_id=current_user_id, message=string, random_id=count)
            count += 1
            # value = vk_api2.messages.getLongPollHistory(ts=current_ts, group_id=my_number_group_id)
    elif message == "stop":
        run = 0
    elif message == "hello" or message == "привет" or message == "Hello" or message == "Привет":
        string = "Ну привет, "
        value = vk_api2.users.get(user_ids=current_user_id, fields='first_name')
        string += value[0]['first_name']
        vk_api2.messages.send(user_id=current_user_id, message=string, random_id=count)
    else:
        string = "I understand just such a format: 'group_id: *id*; period: * period time *'. Please, write correctly))"
        vk_api2.messages.send(user_id=current_user_id, message=string, random_id=count)
        count += 1
