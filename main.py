import vk
import datetime
import requests
import sqlite3 as sql
import group_class as gc
import analyse_and_bot_functions as func
import time
import random
import math

begin_file = "begin_task.txt"

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

some = vk_api2.groups.getLongPollServer(group_id=my_number_group_id)
current_ts = some['ts']
server = some['server']
key = some['key']
change_server = datetime.datetime.now().replace(microsecond=0, second=0) + datetime.timedelta(minutes=30)
message = ""
run = 1
count = 10000
master_id = -1
have_a_task = []
# next_recommend = datetime.datetime.now()
# next_time = datetime.datetime.now()

file = open(begin_file, "r")
task_from_the_previous_session = list(file.read().split('\n'))
for the_task in task_from_the_previous_session:
    task = list(the_task.split())
    if len(task) > 0 and task[0] != '-1':
        this_task = {}
        gr_id = task[0]
        group_object = vk_api2.groups.getById(group_id=gr_id, fields=["id"])
        gr_id = str(group_object[0]['id'])
        usr_id = int(task[1])
        this_task['master'] = usr_id
        rec_hr = int(task[2])
        this_task['group'] = gc.Group(gr_id, usr_id)
        this_task['group'].recommend_hour = rec_hr
        this_task['next_time'], this_task['next_recommend'] = this_task['group'].calculate_new_analyse_time()
        next_time = this_task['next_time']
        hrs = datetime.datetime.now().hour
        if hrs > rec_hr:
            this_task['next_recommend'] = this_task['next_recommend'].replace(hour=rec_hr)
        else:
            this_task['next_recommend'] = this_task['next_recommend'].replace(hour=rec_hr) - datetime.timedelta(days=1)
        have_a_task.append(this_task)
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
        change_server = change_server + datetime.timedelta(minutes=30)

    # chek if it is time to analyse again
    if len(have_a_task) > 0 and datetime.datetime.now() >= next_time:
        next_time += datetime.timedelta(minutes=15)
        for task in have_a_task:
            task['group'].work_and_print()

    # check if it is time to give recommendations
    for task in have_a_task:
        if len(have_a_task) > 0 and datetime.datetime.now() >= task['next_recommend']:
            task['group'].recommendation_for_this_day_of_the_week()
            if datetime.datetime.now().weekday() == 0:
                task['group'].recommendation_for_this_week()
            task['next_recommend'] += datetime.timedelta(days=1)

    code, return_message = func.process_input_message(message)

    if code == 3:
        analyse_group_id = return_message
        group_object = vk_api2.groups.getById(group_id=analyse_group_id, fields=["id"])
        analyse_group_id = str(group_object[0]['id'])
        # this code means that user gave a correct task
        if len(have_a_task) < 10 and func.find_the_task(analyse_group_id, current_user_id, have_a_task) == -1:
            this_task = {}
            # group initialising block
            file = open(begin_file, "r")
            commands = list(file.read().split('\n'))
            file.close()
            file = open(begin_file, "w")
            for command in commands:
                if len(command) > 0 and command[0] != '-':
                    file.write(command + '\n')
            file.write(f"{analyse_group_id} {current_user_id} 0")
            file.close()
            this_task['group'] = gc.Group(analyse_group_id, current_user_id)
            # group.fill_in_index_to_date()
            this_task['master'] = current_user_id
            # counting time when to start and when to give a new recommendation
            this_task['next_time'], this_task['next_recommend'] = this_task['group'].calculate_new_analyse_time()
            if len(have_a_task) == 0:
                next_time = this_task['next_time']
            have_a_task.append(this_task)
        elif len(have_a_task) == 10:
            # in the case when the user wants to give a new task while bot is already working on the OTHER user's task.
            func.cannot_receive_more_tasks(current_user_id)
        else:
            func.have_such_a_task_already(current_user_id)
    elif code == 2:
        # if the bot has received a secret password which switches it off
        run = func.switch_off(current_user_id, have_a_task)
        for x in have_a_task:
            x['group'].del_table()
            del x['group']
        file = open(begin_file, "w")
        file.write("-1 0 0")
        file.close()
    elif code == 1:
        # if the user WHO GAVE A TASK decided to cancel it with a 'stop' or 'Stop' command
        group_object = vk_api2.groups.getById(group_id=return_message, fields=["id"])
        return_message = str(group_object[0]['id'])
        task_number = func.find_the_task(return_message, current_user_id, have_a_task)
        if task_number != -1:
            have_a_task[task_number]['group'].del_table()
            del have_a_task[task_number]['group']
            file = open(begin_file, "r")
            commands = list(file.read().split('\n'))
            file.close()
            file = open(begin_file, "w")
            for cmd_number in range(len(commands)):
                if cmd_number != task_number:
                    file.write(commands[cmd_number] + '\n')
            file.close()
            func.cancel_the_task(have_a_task, task_number, current_user_id)
        else:
            func.no_such_a_task(current_user_id)
    elif code == 4:
        # greeting
        func.say_hello(current_user_id)
    elif code == -1:
        # unknown message
        func.instruction_message(current_user_id)
    elif code == 5:
        # if the group does not exist
        func.incorrect_id(current_user_id)
    elif code == 7:
        # If the user needs today's best online percent and the time it happened
        group_object = vk_api2.groups.getById(group_id=return_message, fields=["id"])
        return_message = str(group_object[0]['id'])
        task_number = func.find_the_task(return_message, current_user_id, have_a_task)
        if task_number != -1:
            have_a_task[task_number]['group'].give_today_stats()
        else:
            func.no_such_a_task(current_user_id)
    elif code == 8:
        # If the user needs week's best online percent and the time it happened
        group_object = vk_api2.groups.getById(group_id=return_message, fields=["id"])
        return_message = str(group_object[0]['id'])
        task_number = func.find_the_task(return_message, current_user_id, have_a_task)
        if task_number != -1:
            have_a_task[task_number]['group'].give_this_week_stats()
        else:
            func.not_such_a_task(current_user_id)
    elif code == 9:
        func.send_big_instruction(current_user_id)
    elif code == 10:
        func.task_by_button(current_user_id)
    elif code == 12:
        group_id = return_message[6:].strip()
        group_object = vk_api2.groups.getById(group_id=group_id, fields=["id"])
        group_id = str(group_object[0]['id'])
        task_number = func.find_the_task(group_id, current_user_id, have_a_task)
        if task_number != -1:
            r_id = func.get_r_id()
            have_a_task[task_number]['next_recommend'] = \
                have_a_task[task_number]['next_recommend'].replace(hour=int(return_message[1: 3]))
            if datetime.datetime.now().hour <= int(return_message[1: 3]):
                have_a_task[task_number]['next_recommend'] -= datetime.timedelta(days=1)
            have_a_task[task_number]['group'].recommend_hour = int(return_message[1: 3])
            vk_api2.messages.send(
                user_id=current_user_id,
                message=f"Отчёты по группе {group_id} буду присылать в {return_message[1:3]}:00!",
                random_id=r_id
            )
            # group.recommend_hour = int(return_message[1: 3])
            func.change_recommend_time(begin_file, task_number, return_message)
        else:
            not func.no_such_a_task(current_user_id)
    elif code == 13:
        func.free_places(current_user_id, len(have_a_task))
    elif code == 14:
        func.send_keyboard(current_user_id)
    elif code == 15:
        func.user_groups(current_user_id, have_a_task)
    elif code == 16:
        func.too_big_group(current_user_id)
    elif code == 17:
        for x in have_a_task:
            if x['master'] == current_user_id:
                x['group'].current_percents = int(return_message)
        r_id = func.get_r_id()
        vk_api2.messages.send(user_id=current_user_id, message="OK", random_id=r_id)
