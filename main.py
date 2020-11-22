import vk
import datetime

token = "65e6efa565e6efa565e6efa54f6593fb1f665e665e6efa53a5c6937a4636b3416a8bd92"
user_id = 't010rd'
session1 = vk.AuthSession(access_token=token)
vk_api = vk.API(session1, v=5.92)


def get_user_last_seen(id):
    """
    shows when user was online
    :param id:
    :return time:
    """
    value = vk_api.users.get(user_ids=id, fields='last_seen')
    online_time = datetime.datetime.fromtimestamp(value[0]['last_seen']['time'])
    return online_time


user_last_online = get_user_last_seen(user_id)
print(user_last_online)
