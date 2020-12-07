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

    def __init__(self, group_id, freq, master_id):
        self.group_id = group_id
        self.master_id = master_id
        self.begin = datetime.datetime.now()
        self.frequency = freq
        self.percents = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.archive = [[0, 0, 0, 0] for i in range(12)]
        self.number = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

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

    def update_data(self, new_one, cell_to_update):
        if self.number[cell_to_update] >= 4:
            self.percents[cell_to_update] *= 4
            self.percents[cell_to_update] = self.percents[cell_to_update] - self.archive[cell_to_update][0] + new_one
            self.percents[cell_to_update] /= 4
        else:
            self.percents[cell_to_update] *= self.number[cell_to_update]
            self.percents[cell_to_update] = self.percents[cell_to_update] + new_one
            self.percents[cell_to_update] /= self.number[cell_to_update]
            self.number[cell_to_update] += 1
        for j in range(3):
            self.archive[cell_to_update][j] = self.archive[cell_to_update][j + 1]
        self.archive[cell_to_update][3] = new_one

    def recommend(self, count):
        recommend_message = "The best time is "
        max_online, best_time = 0, 0
        for i in range(12):
            if self.percents[i] > max_online:
                max_online = self.percents[i]
                best_time = i
        best_time *= self.frequency
        recommend_message += str(best_time) + " minutes: " + str(max_online) + "%"
        vk_api2.messages.send(user_id=self.master_id, message=recommend_message, random_id=count)
        return count + 1

    def work_and_print(self, count, current_user_id):
        array_cell = datetime.datetime.now().minute // self.frequency
        start_time, percent = self.group_analyse()
        self.update_data(percent, array_cell)
        string = "Online percent in " + self.group_id + " is " + str(percent) + "%"
        vk_api2.messages.send(user_id=current_user_id, message=string, random_id=count)
        return count + 1

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


def handle_input_message(message):
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
        if not period.isdigit() and not period == "frequently":
            return -1, "", -1
        elif period == "frequently":
            return 3, group, 0
        else:
            return 3, group, int(period)
    string1 = message[0: 6]
    string2 = message[0: 5]
    if string1 == "Привет" or string1 == "привет" or string2 == "Hello" or string2 == "hello":
        return 4, "", -1
    return -1, "", -1


def switch_off(count, current_user_id):
    # switches the bot off, the special password is needed
    vk_api2.messages.send(user_id=current_user_id, message="Goodbye!", random_id=count)
    return 0, count + 1


def incorrect_id(count, current_user_id):
    # informs about the mistake
    vk_api2.messages.send(user_id=current_user_id, message="Wrong group id!", random_id=count)
    return count + 1


def cancel_the_task(have_a_task, current_user_id, count, master_id):
    # Cancels the current task, it is is asked by the user who gave the task earlier
    if have_a_task and current_user_id == master_id:
        vk_api2.messages.send(user_id=current_user_id, message="Your task is cancelled!", random_id=count)
        return 0, count + 1
    elif have_a_task:
        vk_api2.messages.send(user_id=current_user_id, message="Sorry, I am working on the other user's task!",
                              random_id=count)
        return 1, count + 1
    else:
        vk_api2.messages.send(user_id=current_user_id, message="Я сделал ничего, не благодари!",
                              random_id=count)
        return 0, count + 1


def say_hello(count, current_user_id):
    # sends a message 'Ну привет, ....'
    string = "Ну привет, "
    value = vk_api2.users.get(user_ids=current_user_id, fields='first_name')
    string += value[0]['first_name']
    vk_api2.messages.send(user_id=current_user_id, message=string, random_id=count)
    return count + 1


def instruction_message(count, current_user_id):
    # sends the message if user did send us the message of an unknown format
    string = "I am really sorry but i don't understand you. I know the format: 'group_id: ...; period: ...' Be careful!"
    vk_api2.messages.send(user_id=current_user_id, message=string, random_id=count)
    return count + 1


def repeat_the_process(master_id, count, next_time):
    # current_minutes = time_start.minute
    next_time = count_new_time(next_time, group.frequency)
    count = group.work_and_print(count, master_id)
    return next_time, count


def first_process(count, master_id, group):
    t0 = time.time()
    time_start = datetime.datetime.now()
    next_time = count_new_time(time_start, group.frequency)
    # next_minutes - when to count again
    count = group.work_and_print(count, master_id)
    t0 = time.time() - t0
    # if analysing took more time than the period:
    if t0 > group.frequency * 60:
        vk_api2.messages.send(user_id=master_id, message="Can't work so fast((",
                              random_id=count)
        next_time = datetime.datetime.now()
        group.frequency = 0
        return next_time, count + 1
    return next_time, count


def check_for_correct(group_id):
    try:
        your_group_info = vk_api.groups.getById(group_id=group_id, fields='members_count', count=1)
    except vk.exceptions.VkAPIError:
        return 0
    return 1


# starts working, gives default values to some variables

some = vk_api2.groups.getLongPollServer(group_id=my_number_group_id)
current_ts = some['ts']
server = some['server']
key = some['key']
message = ""
run = 1
count = 0
have_a_task = 0
group = Group(-1, -1, -1)
master_id = -1
next_recommend = datetime.datetime.now()
next_time = datetime.datetime.now()

# the end of 'initialization' block

while run:
    message, current_user_id, current_ts = get_message(my_number_group_id, server, current_ts, key)
    if have_a_task and datetime.datetime.now() >= next_time:
        next_time, count = repeat_the_process(master_id, count, next_time)
    if have_a_task and datetime.datetime.now() >= next_recommend:
        count = group.recommend(count)
        next_recommend = count_new_time(next_recommend, 60)

    code, analyse_group_id, frequency_number = handle_input_message(message)

    if code == 3:
        if not have_a_task or current_user_id == master_id:
            have_a_task = 1
            master_id = current_user_id
            group.group_id = analyse_group_id
            group.frequency = frequency_number
            group.master_id = master_id
            # To start not at 17:48 but at 17:50, for example
            minutes_now = datetime.datetime.now().minute
            ok_message = "OK! Starting in " + str(group.frequency - minutes_now % group.frequency) + " minutes!"
            vk_api2.messages.send(user_id=current_user_id, message=ok_message, random_id=count)
            count += 1
            next_time = count_new_time(datetime.datetime.now(), group.frequency - minutes_now % group.frequency)
            current_time = datetime.datetime.now()
            next_recommend = current_time.replace(microsecond=0, second=0, minute=0)
            next_recommend = count_new_time(next_recommend, 60)
        else:
            vk_api2.messages.send(user_id=current_user_id, message="Sorry, I am busy!", random_id=count)
            count += 1
    elif code == 2:
        run, count = switch_off(count, current_user_id)
    elif code == 1:
        have_a_task, count = cancel_the_task(have_a_task, current_user_id, count, master_id)
    elif code == 4:
        count = say_hello(count, current_user_id)
    elif code == -1:
        count = instruction_message(count, current_user_id)
    elif code == 5:
        count = incorrect_id(count, current_user_id)
