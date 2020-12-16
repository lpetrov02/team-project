import vk
import datetime
import requests
import time
import random
import math


class Group:
    def __init__(self, group_id, freq, master_id):
        """
          group_id: the group to analyse
          master_id: id of the user who gave the task
          frequency: how many minutes should pass between two adjoining analyses
          analyses_per_day: daily amount of analyses
          percents: online percents in each 'moment' of the week (not more than 672 moments)
          archive: old data, we need this to delete old info whe 4 weeks pass
          number: technical moment. Actually, first three weeks are special: to count the average meaning we need not to
        divide by 4, but to divide by the number - spacial for each array cell.
        Just because we don't have enough information yet!!
          index_to_date: in the storage we keep the moment of time as a code - gust an integer number. But the user
        would prefer 'Mon, 00:00: 30%' to '0: 30%'. That's why we need this array
        """
        self.group_id = group_id
        self.master_id = master_id
        self.frequency = freq
        self.analyses_per_day = 1440 // self.frequency
        analyses_per_week = self.analyses_per_day * 7
        self.percents = [0 for i in range(analyses_per_week)]
        self.archive = [[0, 0, 0, 0] for i in range(analyses_per_week)]
        self.number = [0 for i in range(analyses_per_week)]
        self.index_to_date = []
        for i in range(analyses_per_week):
            week_day = i // self.analyses_per_day
            time_index = i % self.analyses_per_day * self.frequency
            hour_index = time_index // 60
            minute_index = time_index % 60
            s = days_of_the_week[week_day] + ", " + str(hour_index) + ":" + str(minute_index)
            if minute_index == 0:
                s += '0'
            self.index_to_date.append(s)

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
        """
        counts the online percent
        :return:
        """
        t0 = time.time()

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
            self.number[cell_to_update] += 1
            self.percents[cell_to_update] /= self.number[cell_to_update]
        for j in range(3):
            self.archive[cell_to_update][j] = self.archive[cell_to_update][j + 1]
        self.archive[cell_to_update][3] = new_one

    def recommend_day(self):
        # average stats and recommendation for this day of the week past 4 last weeks
        r_id = get_r_id(self.master_id)
        day = datetime.datetime.now().weekday()
        start = day * self.analyses_per_day
        finish = (day + 1) * self.analyses_per_day
        recommend_message = "Today the best time was "
        max_online, best_time = 0, 0
        for i in range(start, finish):
            if self.percents[i] > max_online:
                max_online = self.percents[i]
                best_time = i
        recommend_message += self.index_to_date[best_time] + ": " + str(max_online) + "%"
        vk_api2.messages.send(user_id=self.master_id, message=recommend_message, random_id=r_id)
        return

    def recommend_week(self):
        # recommendation gives the day with the highest average percents past 4 last weeks
        r_id = get_r_id(self.master_id)
        recommend_message = "This week the best time was "
        max_online, best_time, max_average_during_the_day, best_day = 0, 0, 0, 0
        for j in range(7):
            average = 0
            for i in range(self.analyses_per_day * j, self.analyses_per_day * (j + 1)):
                average += self.percents[i]
                if self.percents[i] > max_online:
                    max_online = self.percents[i]
                    best_time = i
            if average > max_average_during_the_day:
                max_average_during_the_day = average
                best_day = j
        max_average_during_the_day /= self.analyses_per_day
        recommend_message += self.index_to_date[best_time] + ": " + str(max_online) + "%"
        vk_api2.messages.send(user_id=self.master_id, message=recommend_message, random_id=r_id)
        recommend_message = "This week, the day with the biggest average online percent was " + \
                            days_of_the_week[best_day] + ": " + str(max_average_during_the_day) + "%"
        vk_api2.messages.send(user_id=self.master_id, message=recommend_message, random_id=(r_id + 1))
        return

    def recommend_certain_day(self):
        # Just today's stats
        r_id = get_r_id(self.master_id)
        day = datetime.datetime.now().weekday()
        start = day * self.analyses_per_day
        finish = (day + 1) * self.analyses_per_day
        recommend_message = "Today the best time was "
        max_online, best_time = 0, 0
        for i in range(start, finish):
            if self.archive[i][3] > max_online:
                max_online = self.archive[i][3]
                best_time = i
        recommend_message += self.index_to_date[best_time] + ": " + str(max_online) + "%"
        vk_api2.messages.send(user_id=self.master_id, message=recommend_message, random_id=r_id)
        return

    def recommend_certain_week(self):
        # Just this week stats
        r_id = get_r_id(self.master_id)
        recommend_message = "This week the best time was "
        max_online, best_time, max_average_during_the_day, best_day = 0, 0, 0, 0
        for j in range(7):
            average = 0
            for i in range(self.analyses_per_day * j, self.analyses_per_day * (j + 1)):
                average += self.archive[i][3]
                if self.archive[i][3] > max_online:
                    max_online = self.aechive[i][3]
                    best_time = i
            if average > max_average_during_the_day:
                max_average_during_the_day = average
                best_day = j
        max_average_during_the_day /= self.analyses_per_day
        recommend_message += self.index_to_date[best_time] + ": " + str(max_online) + "%"
        vk_api2.messages.send(user_id=self.master_id, message=recommend_message, random_id=r_id)
        recommend_message = "This week, the day with the biggest average online percent was " + \
                            days_of_the_week[best_day] + ": " + str(max_average_during_the_day) + "%"
        vk_api2.messages.send(user_id=self.master_id, message=recommend_message, random_id=(r_id + 1))
        return

    def work_and_print(self):
        """
        updates data and sends current online percent
        :param count - is needed to send messages:
        :return:
        """
        r_id = get_r_id(self.master_id)
        week_day = datetime.datetime.now().weekday()
        t = datetime.datetime.now()
        array_cell = self.analyses_per_day * week_day + (t.hour * 60 + t.minute) // self.frequency
        start_time, percent = self.group_analyse()
        self.update_data(percent, array_cell)
        string = "Online percent in " + self.group_id + " is " + str(percent) + "%"
        vk_api2.messages.send(user_id=self.master_id, message=string, random_id=r_id)
        return

    def repeat_the_process(self, next_time):
        """
        :param count - is needed to send messages to the user:
        :param next_time - when to analyse again:
        :return:
        """
        next_time = count_new_time(next_time, self.frequency)
        self.work_and_print()
        return next_time

    def count_times(self):
        """
        This function runs in the very beginning. It counts when to start analysing and when to give recommendations
        """
        r_id = get_r_id(self.master_id)
        current_time = datetime.datetime.now()
        minutes_now = current_time.minute + current_time.hour * 60
        round_current_time = current_time.replace(microsecond=0, second=0)
        next_time = count_new_time(round_current_time, self.frequency - minutes_now % self.frequency)
        next_recommend = current_time.replace(microsecond=0, second=0, minute=0, hour=0)
        next_recommend = count_new_time(next_recommend, 1440)
        ok_message = "OK! Starting in " + str(self.frequency - minutes_now % self.frequency) + " minutes!"
        vk_api2.messages.send(user_id=self.master_id, message=ok_message, random_id=r_id)
        return next_time, next_recommend



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
        return 0
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


# starts working, gives default values to some variables

some = vk_api2.groups.getLongPollServer(group_id=my_number_group_id)
current_ts = some['ts']
server = some['server']
key = some['key']
change_server = count_new_time(datetime.datetime.now().replace(microsecond=0, second=0), 50)
message = ""
run = 1
count = 10000
master_id = -1
have_a_task = 0
next_recommend = datetime.datetime.now()
next_time = datetime.datetime.now()

# the end of 'initialization' block

while run:
    # wait for new requests
    message, current_user_id, current_ts = get_message(my_number_group_id, server, current_ts, key)

    # if it is time to change LongPollServer
    if datetime.datetime.now() >= change_server:
        some = vk_api2.groups.getLongPollServer(group_id=my_number_group_id)
        current_ts = some['ts']
        server = some['server']
        key = some['key']
        change_server = count_new_time(change_server, 50)

    # chek if it is time to analyse again
    if have_a_task and datetime.datetime.now() >= next_time:
        next_time = group.repeat_the_process(next_time)

    # check if it is time to give recommendations
    if have_a_task and datetime.datetime.now() >= next_recommend:
        group.recommend_day()
        if datetime.datetime.now().weekday() == 0:
            group.recommend_week()
        next_recommend = count_new_time(next_recommend, 1440)

    code, analyse_group_id, frequency_number = process_input_message(message)

    if code == 3:
        # this code means that user gave a correct task
        if not have_a_task or current_user_id == master_id:
            '''
            if the bot is free or is working on the task of the same user, who is giving a new one. In this case
            bot receives a new task and forgets about the old one if it did exist
            '''
            have_a_task = 1
            # group initialising block
            group = Group(analyse_group_id, frequency_number, current_user_id)
            master_id = group.master_id
            # counting time when to start and when to give a new recommendation
            next_time, next_recommend = group.count_times()
        else:
            # in the case when the user wants to give a new task while bot is already working on the OTHER user's task.
            not_available(current_user_id)
    elif code == 2:
        # if the bot has received a secret password which switches it off
        run = switch_off(current_user_id)
    elif code == 1:
        # if the user WHO GAVE A TASK decided to cancel it with a 'stop' or 'Stop' command
        if have_a_task:
            del group
        have_a_task = cancel_the_task(have_a_task, current_user_id, master_id)
    elif code == 4:
        # greeting
        say_hello(current_user_id)
    elif code == -1:
        # unknown message
        instruction_message(current_user_id)
    elif code == 5:
        # if the group does not exist
        incorrect_id(current_user_id)
    elif code == 6:
        '''
        if the period doesn't divide 60 (if it is less than 60) or if it doesn't divide 1440 
        (number of minutes in a day)
        '''
        incorrect_period_value(current_user_id)
    elif code == 7:
        # If the user needs today's best online percent and the time it happened
        if have_a_task and current_user_id == master_id:
            group.recommend_certain_day()
        else:
            not_available(current_user_id)
    elif code == 8:
        # If the user needs week's best online percent and the time it happened
        if have_a_task and current_user_id == master_id:
            group.recommend_certain_week()
        else:
            not_available(current_user_id)

