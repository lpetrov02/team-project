import vk
import requests
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
import pylab as pltt
import datetime
import matplotlib.dates as mdates




token = "812c2975fc2ac0785252d97e8b5011f45e873a00dfb98b15299aec060ff7b890d06c4822feab0626e198c"
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
    figure, ax = plt.subplots(figsize=(number_of_dots/5, 10))
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
