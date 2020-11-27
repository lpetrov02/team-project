import vk
import datetime
import time
import random


class Group:
    def __init__(self, group_id, freq):
        self.group_id = group_id
        self.begin = datetime.datetime.now()
        self.frequency = freq

    def fast_online(self):
        amount = 0
        online = 0
        your_group = vk_api.groups.getById(group_id=self.group_id, fields='members_count')
        number_of_them = your_group[0]['members_count']
        one_more_number_of_them = number_of_them
        done = 0
        while done < number_of_them:
            group_members_ids = vk_api.groups.getMembers(group_id=self.group_id, offset=done, fields='online')
            for x in group_members_ids['items']:
                if 'online' in x:
                    online += x['online']
                else:
                    one_more_number_of_them -= 1
            done += 1000
        if one_more_number_of_them == 0:
            return -1, -1
        else:
            return one_more_number_of_them, online


token = "65e6efa565e6efa565e6efa54f6593fb1f665e665e6efa53a5c6937a4636b3416a8bd92"
user_id = 'memkn'
session1 = vk.AuthSession(access_token=token)
vk_api = vk.API(session1, v=5.92)

month_length = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def get_user_last_seen(id):
    """
    shows when user was online
    :param id:
    :return time:
    """
    value = vk_api.users.get(user_ids=id, fields='last_seen')
    if 'last_seen' not in value[0]:
        return None
    online_time = datetime.datetime.fromtimestamp(value[0]['last_seen']['time'])
    return online_time


def get_group_followers(id, done):
    """
    shows when user was online
    :param id:
    :return time:
    """
    value = vk_api.groups.getMembers(group_id=id, offset=done)
    followers_id = []
    for user in value['items']:
        followers_id.append(user)
    return followers_id


def get_user_followers(id):
    """
    shows when user was online
    :param id:
    :return time:
    """
    value = vk_api.users.getFollowers(user_id=id)
    followers_id = []
    for user in value['items']:
        followers_id.append(user)
    return followers_id


def delta_time(real_time):
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

    tipa_online_time = real_time.replace(minute=(real_time.minute + 2) % 60,
                                         hour=hours, day=days, month=months, year=years)
    return tipa_online_time


def is_online(online_time):
    now_time = datetime.datetime.now()
    now_time = now_time.replace(microsecond=0)
    if online_time >= now_time:
        return 1
    else:
        return 0


def count_online(id):
    amount = 0
    online = 0
    your_group = vk_api.groups.getById(group_id=id, fields='members_count')
    number_of_them = your_group[0]['members_count']
    if number_of_them <= 10000:
        done = 0
        while done < number_of_them:
            group_members_ids = get_group_followers(id, done)
            for x in group_members_ids:
                last = get_user_last_seen(str(x))
                if last is not None:
                    amount += 1
                    delta_last = delta_time(last)
                    online += is_online(delta_last)
            done += 1000
        if amount == 0:
            return -1
        else:
            return amount, online
    else:
        piece = number_of_them // 100
        for i in range(piece):
            group_members_ids = get_group_followers(id, 100 * i)
            x = random.randint(0, 100)
            last = get_user_last_seen(str(group_members_ids[x]))
            if last is not None:
                amount += 1
                delta_last = delta_time(last)
                online += is_online(delta_last)
        number_of_them -= piece * 100
        group_members_ids = get_group_followers(id, piece * 100)
        x = random.randint(0, number_of_them - 1)
        last = get_user_last_seen(str(group_members_ids[x]))
        if last is not None:
            amount += 1
            delta_last = delta_time(last)
            online += is_online(delta_last)
        return amount, online


group = Group(user_id, 30)
all_members, online_members = group.fast_online()
# all_members1, online_members1 = count_online(user_id)
percent = online_members / all_members * 100
# percent1 = online_members1 / all_members1 * 100

print("In this group i have got information about " + str(all_members) + " users")
# print("In this group i have got information about " + str(all_members1) + " users")

print("Online percent in " + user_id + " is " + str(percent))
vk_api.Messages.message.send(user_id=427479334, message="Online percent in " + user_id + " is " + str(percent))
# print("Online percent is " + str(percent1))
