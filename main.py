import vk
import datetime


token = "65e6efa565e6efa565e6efa54f6593fb1f665e665e6efa53a5c6937a4636b3416a8bd92"
user_id = 'memkn'
session1 = vk.AuthSession(access_token=token)
vk_api = vk.API(session1, v=5.92)


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


def get_group_followers(group_page_id):
    """
    shows when user was online
    :param group_page_id:
    :return list of followers id:
    """
    value = vk_api.groups.getMembers(group_id=group_page_id)
    followers_id = []
    for user in value['items']:
        followers_id.append(user)
    return followers_id


def approximate_time(real_time):
    approximated_online_time = real_time.replace(minute=(real_time.minute + 2) % 60)
    return approximated_online_time


def is_online(online_time):
    now_time = datetime.datetime.now()
    now_time = now_time.replace(microsecond=0)
    if online_time >= now_time:
        return 1
    else:
        return 0


def online_proportion(group_id):
    group_members_ids = get_group_followers(group_id)
    group_amount = 0
    group_online = 0
    for profile in group_members_ids:
        profile_last_seen = get_user_last_seen(str(profile))
        if profile_last_seen is not None:
            group_amount += 1
            profile_last_seen = approximate_time(profile_last_seen)
            group_online += is_online(profile_last_seen)
    if group_amount == 0:
        return -1
    else:
        percent_online = group_online / group_amount * 100
        return percent_online


print(online_proportion(user_id))
