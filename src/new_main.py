import vk
import datetime
import requests
import sqlite3 as sql
import src.group_class_with_db as gc
import src.analyse_and_bot_functions as func
import time
import random
import math

begin_file = "../data/begin_task.txt"

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

# starts working, gives default values to some variables

# чисто технический момент с сервером
some = vk_api2.groups.getLongPollServer(group_id=my_number_group_id)
current_ts = some['ts']
server = some['server']
key = some['key']
# сервер получен

change_server = datetime.datetime.now().replace(microsecond=0, second=0) + datetime.timedelta(minutes=30)
message = ""
run = 1
count = 10000
master_id = -1
have_a_task = 0
next_recommend = datetime.datetime.now()
next_time = datetime.datetime.now()

file = open(begin_file, "r")
task_from_the_previous_session = list(file.readline().split())
if len(task_from_the_previous_session) > 0 and task_from_the_previous_session[0] != '-1':
    gr_id = task_from_the_previous_session[0]
    usr_id = int(task_from_the_previous_session[1])
    prd = int(task_from_the_previous_session[2])
    rec_hr = int(task_from_the_previous_session[3])
    have_a_task = 1
    group = gc.Group(gr_id, prd, usr_id)
    group.recommend_hour = rec_hr
    master_id = usr_id
    next_time, next_recommend = group.calculate_new_analyse_time()
    hrs = datetime.datetime.now().hour
    if hrs > rec_hr:
        next_recommend = next_recommend.replace(hour=rec_hr)
    else:
        next_recommend = next_recommend.replace(hour=rec_hr) - datetime.timedelta(days=1)
file.close()

# the end of 'initialization' block

while run:
    # wait for new requests
    message, current_user_id, current_ts = func.get_message(my_number_group_id, server, current_ts, key)

    # if it is time to change LongPollServer
    if datetime.datetime.now() >= change_server:
        some = vk_api2.groups.getLongPollServer(group_id=my_number_group_id)
        current_ts = some['ts']
        server = some['server']
        key = some['key']
        change_server += datetime.timedelta(minutes=30)

    # chek if it is time to analyse again
    if have_a_task and datetime.datetime.now() >= next_time:
        next_time = group.analyse(next_time)

    # check if it is time to give recommendations
    if have_a_task and datetime.datetime.now() >= next_recommend:
        group.recommendation_for_this_day_of_the_week()
        if datetime.datetime.now().weekday() == 0:
            group.recommendation_for_this_week()
        next_recommend += datetime.timedelta(days=1)

    code, return_message, return_number = func.process_input_message(message)

    if code == 3:
        frequency_number = return_number
        analyse_group_id = return_message
        # this code means that user gave a correct task
        if not have_a_task or current_user_id == master_id:
            '''
            if the bot is free or is working on the task of the same user, who is giving a new one. In this case
            bot receives a new task and forgets about the old one if it did exist
            '''
            have_a_task = 1
            # group initialising block
            file = open(begin_file, "w")
            file.write(f"{analyse_group_id} {current_user_id} {frequency_number} 0")
            file.close()
            group = gc.Group(analyse_group_id, frequency_number, current_user_id)
            # group.fill_in_index_to_date()
            master_id = group.master_id
            # counting time when to start and when to give a new recommendation
            next_time, next_recommend = group.calculate_new_analyse_time()
        else:
            # in the case when the user wants to give a new task while bot is already working on the OTHER user's task.
            func.not_available(current_user_id)
    elif code == 2:
        # if the bot has received a secret password which switches it off
        if have_a_task:
            group.del_table()
        func.switch_off(current_user_id, begin_file)
        run = 0
    elif code == 1:
        # if the user WHO GAVE A TASK decided to cancel it with a 'stop' or 'Stop' command
        if have_a_task and current_user_id == master_id:
            group.del_table()
            del group
        func.cancel_the_task(have_a_task, current_user_id, master_id, begin_file)
        have_a_task = 0
    elif code == 4:
        # greeting
        func.say_hello(current_user_id)
    elif code == -1:
        # unknown message
        func.instruction_message(current_user_id)
    elif code == 5:
        # if the group does not exist
        func.incorrect_id(current_user_id)
    elif code == 6:
        '''
        if the period doesn't divide 60 (if it is less than 60) or if it doesn't divide 1440 
        (number of minutes in a day)
        '''
        func.incorrect_period_value(current_user_id)
    elif code == 7:
        # If the user needs today's best online percent and the time it happened
        if have_a_task and current_user_id == master_id:
            group.give_today_stats()
        else:
            func.not_available(current_user_id)
    elif code == 8:
        # If the user needs week's best online percent and the time it happened
        if have_a_task and current_user_id == master_id:
            group.give_this_week_stats()
        else:
            func.not_available(current_user_id)
    elif code == 9:
        func.send_big_instruction(current_user_id)
    elif code == 10:
        func.task_by_button(current_user_id)
    elif code == 11:
        func.set_time(current_user_id)
    elif code == 12:
        if have_a_task and current_user_id == master_id:
            r_id = func.get_new_random_id()
            next_recommend = next_recommend.replace(hour=int(return_message[1: 3]))
            if datetime.datetime.now().hour <= int(return_message[1: 3]):
                next_recommend -= datetime.timedelta(days=1)
            vk_api2.messages.send(
                user_id=current_user_id,
                message=f"I'll send recommendations at {return_message[1:]}!",
                random_id=r_id
            )
            group.recommend_hour = int(return_message[1: 3])
            file = open(begin_file, "w")
            file.write(f"{group.group_id} {group.master_id} {group.period} {group.recommend_hour}")
            file.close()
        else:
            not func.not_available(current_user_id)
    elif code == 13:
        if have_a_task and current_user_id == master_id:
            stats_dict = group.daily_graph_request(return_number)
            stats_dict = func.dict_with_strings_to_dict_for_plots(stats_dict)
            ph_id = "photos" + str(current_user_id) + \
                    datetime.datetime.now().day + datetime.datetime.now().hour + \
                    datetime.datetime.now().minute + datetime.datetime.now().second
            func.create_daily_image(stats_dict, ph_id)
            res_url = func.upload_picture(f'../data/image/{ph_id}')
            stop_ind = res_url.find('%')
            vk_api2.messages.send(
                user_id=current_user_id,
                message=f"Get it!",
                random_id=r_id,
                attachment=res_url[32: stop_ind]
            )
