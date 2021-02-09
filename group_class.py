import vk
import datetime
import sqlite3 as sql
import requests
import time
import random
import analyse_and_bot_functions as func
import math

# from new_main import vk_api2 as vk_api2
# from new_main import days_of_the_week as days_of_the_week

con = sql.connect('super_vk_bot3.db')
cur = con.cursor()

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


class Group:
    def __init__(self, group_id, master_id):
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
        self.recommend_hour = 0
        self.group_id = group_id
        group_object = vk_api2.groups.getById(group_id=group_id, fields=["name"])
        self.name = str(group_object[0]['name'])
        self.master_id = master_id
        self.period = 15
        self.analyses_per_day = 96
        self.current_percents = 1

        # con = sql.connect('vk_bot.db')
        name = "stats" + str(self.group_id) + str(self.master_id)
        with con:
            # cur = con.cursor()
            cur.execute(f"CREATE TABLE IF NOT EXISTS {name} ("
                        "'analyse_number' INTEGER PRIMARY KEY, "
                        "'average_percent' INTEGER, "
                        "'archive1' INTEGER, "
                        "'archive2' INTEGER, "
                        "'archive3' INTEGER, "
                        "'archive4' INTEGER, "
                        "'weeks_passed' INTEGER, "
                        "'time' STRING"
                        ")"
                        )
            sq = f"SELECT * FROM {name} WHERE analyse_number={0}"
            cur.execute(sq)
            table_existed = cur.fetchone()
            con.commit()
            if table_existed is None or table_existed == []:
                for j in range(7):
                    for i in range(self.analyses_per_day * j, self.analyses_per_day * (j + 1)):
                        s = days_of_the_week[j] + ", "
                        hours = (i % self.analyses_per_day) * self.period // 60
                        minutes = (i % self.analyses_per_day) * self.period % 60
                        if hours < 10:
                            s += "0"
                        s += str(hours) + ":"
                        if minutes < 10:
                            s += "0"
                        s += str(minutes)
                        stats = (i, 0, 0, 0, 0, 0, 0, s)
                        cur.execute(f"""INSERT OR REPLACE INTO {name} VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", stats)
                    con.commit()

    def del_table(self):
        # con = sql.connect('vk_bot.db')
        name = "stats" + str(self.group_id) + str(self.master_id)
        # cur = con.cursor()
        cur.execute(f"""DELETE FROM {name}""")
        con.commit()

    def count_online_proportion(self):
        """
        gets the number of members online, ant the total number of members, not counting those,
        whose info is not is not available
        :param self: the object of the class Group. We need the group id
        :return: two integers - the number of members with available online-information and the number of members online
        """
        online = 0
        your_group_info = vk_api.groups.getById(group_id=self.group_id, fields='members_count')
        number_of_members = your_group_info[0]['members_count']
        number_of_members1 = number_of_members
        already_count = 0
        while already_count < number_of_members:
            group_members_ids = vk_api.groups.getMembers(group_id=self.group_id, offset=already_count, fields='online')
            for x in group_members_ids['items']:
                if 'online' in x:
                    online += x['online']
                else:
                    number_of_members1 -= 1
            already_count += 1000
        if number_of_members1 == 0:
            return -1, -1
        else:
            return number_of_members1, online

    def group_analyse(self):
        """
        counts the online percent
        :return:
        """
        all_members, online_members = self.count_online_proportion()
        percent = online_members / all_members * 100
        percent = math.ceil(percent)

        return percent

    def update_data(self, new_one, cell_to_update):
        # con = sql.connect('vk_bot.db')
        # cur = con.cursor()
        name = "stats" + str(self.group_id) + str(self.master_id)

        sq = f"SELECT * FROM {name} WHERE analyse_number={cell_to_update}"
        cur.execute(sq)
        values_arr = cur.fetchall()
        values_tuple = values_arr[0]
        values = []
        for i in range(7):
            values.append(values_tuple[i])
        print(values)
        if values[6] >= 4:
            values[1] *= 4
            values[1] = values[1] - values[2] + new_one
            values[1] /= 4
        else:
            values[1] *= values[6]
            values[1] += new_one
            values[6] += 1
            values[1] /= values[6]
        for j in range(3):
            values[2 + j] = values[3 + j]
        values[5] = new_one

        stats = (values[0], values[1], values[2], values[3], values[4], values[5], values[6], values_tuple[7])
        cur.execute(f"""INSERT OR REPLACE INTO {name} VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", stats)
        con.commit()

    def recommendation_for_this_day_of_the_week(self):
        """
        this function runs at about 00:00 daily and recommends: when it is going to be the best time for posts this day.
        :return: returns nothing, just sends a message with recommendation
        """
        # average stats and recommendation for this day of the week past 4 last weeks

        # con = sql.connect('vk_bot.db')
        # cur = con.cursor()
        name = "stats" + str(self.group_id) + str(self.master_id)

        r_id = func.get_r_id()

        today_or_tomorrow = "сегодня"
        day = datetime.datetime.now().weekday()
        if self.recommend_hour != 0:
            day = (day + 1) % 7
            today_or_tomorrow = "завтра"

        start = day * self.analyses_per_day
        finish = (day + 1) * self.analyses_per_day
        check = 0

        for t in range(start, finish):
            sq = f"SELECT weeks_passed FROM {name} WHERE analyse_number={t}"
            cur.execute(sq)
            checker = cur.fetchone()
            check += checker[0]
        if check == 0:  # Если за этот день недели вообще нет данных
            day = (day - 1) % 7  # то возьмём данные за предыдущий день
            start = day * self.analyses_per_day
            finish = (day + 1) * self.analyses_per_day

        recommend_message = f"Вероятно, {today_or_tomorrow} лучше всего выкладывать посты в группе " + \
                            f"'{self.name}' в "
        max_online, best_time = 0, 0
        for i in range(start, finish):
            sq = f"SELECT average_percent FROM {name} WHERE analyse_number={i}"
            cur.execute(sq)
            current_percent = cur.fetchone()[0]
            if current_percent > max_online:
                max_online = current_percent
                best_time = i

        sq = f"SELECT time FROM {name} WHERE analyse_number={best_time}"
        cur.execute(sq)
        recommend_time = cur.fetchone()[0]
        recommend_message += recommend_time[5:] + ": " + str(max_online) + "%"
        vk_api2.messages.send(user_id=self.master_id, message=recommend_message, random_id=r_id)
        return

    def get_one_day_information_v1(
            self, day, max_summary_percent, day_with_the_highest_summary_percent, best_time, max_online
    ):
        """
        function to look for highest percents between average percents on a week
        :param day: the number of the day to get information about
        :param max_summary_percent: the day withe the highest summary online percent
         (among those that we have already checked). So, it is the current highest percent for a day.
        :param day_with_the_highest_summary_percent: Number of the day when the 'max_summary_percent' was fixed
        :param best_time: the moment of time withe highest online percent during the week
        :param max_online: that highest percent
        :return: updated 'max_summary_percent', 'day_with_the_highest_summary_percent', 'best_time' and 'max_online'
        """
        # needed for 'recommendation_for_this_week'

        # con = sql.connect('vk_bot.db')
        # cur = con.cursor()
        name = "stats" + str(self.group_id) + str(self.master_id)

        summary_percents = 0
        for i in range(self.analyses_per_day * day, self.analyses_per_day * (day + 1)):
            sq = f"SELECT average_percent FROM {name} WHERE analyse_number={i}"
            cur.execute(sq)
            current_percent = cur.fetchone()[0]
            summary_percents += current_percent
            if current_percent > max_online:
                max_online = current_percent
                best_time = i
        if summary_percents > max_summary_percent:
            return summary_percents, day, best_time, max_online
        return max_summary_percent, day_with_the_highest_summary_percent, best_time, max_online

    def get_one_day_information_v2(
            self, day, max_summary_percent, day_with_the_highest_summary_percent, best_time, max_online
    ):
        # needed for 'give_this_week_stats'
        """
               function to look for highest percents between certain percents on the current week
               :param day: the number of the day to get information about
               :param max_summary_percent: the day withe the highest summary online percent
                (among those that we have already checked). So, it is the current highest percent for a day.
               :param day_with_the_highest_summary_percent: Number of the day when the 'max_summary_percent' was fixed
               :param best_time: the moment of time withe highest online percent during the week
               :param max_online: that highest percent
               :return: updated 'max_summary_percent', 'day_with_the_highest_summary_percent', 'best_time' and 'max_online'
               """
        # needed for 'recommendation_for_this_week'

        # con = sql.connect('vk_bot.db')
        # cur = con.cursor()
        name = "stats" + str(self.group_id) + str(self.master_id)

        summary_percents = 0
        for i in range(self.analyses_per_day * day, self.analyses_per_day * (day + 1)):
            sq = f"SELECT archive4 FROM {name} WHERE analyse_number={i}"
            cur.execute(sq)
            current_percent = cur.fetchone()[0]
            summary_percents += current_percent
            if current_percent > max_online:
                max_online = current_percent
                best_time = i
        if summary_percents > max_summary_percent:
            return summary_percents, day, best_time, max_online
        return max_summary_percent, day_with_the_highest_summary_percent, best_time, max_online

    def recommendation_for_this_week(self):
        """
        function that runs weekly at about 00:00 and sends two messages: day withe the highest average percent and
        time(with a day) when the percent was highest
        Takes average percents for last four weeks
        :return: nothing
        """
        # recommendation gives the day with the highest average percents past 4 last weeks

        # con = sql.connect('vk_bot.db')
        # cur = con.cursor()
        name = "stats" + str(self.group_id) + str(self.master_id)

        r_id = func.get_r_id()
        recommend_message = f"Вероятно, на этой неделе лучшим временем для постов в группе '{self.name}' будет "
        max_online, best_time, max_summary_during_the_day, best_day = 0, 0, 0, 0

        for j in range(7):
            max_summary_during_the_day, best_day, best_time, max_online = \
                self.get_one_day_information_v1(j, max_summary_during_the_day, best_day, best_time, max_online)
        max_average_during_the_day = max_summary_during_the_day / self.analyses_per_day

        sq = f"SELECT time FROM {name} WHERE analyse_number={best_time}"
        cur.execute(sq)
        recommend_time = cur.fetchone()[0]
        recommend_message += recommend_time + ": " + str(max_online) + "%"

        vk_api2.messages.send(user_id=self.master_id, message=recommend_message, random_id=r_id)
        recommend_message = "This week, the day with the biggest average online percent was " + \
                            days_of_the_week[best_day] + ": " + str(max_average_during_the_day) + "%"
        vk_api2.messages.send(user_id=self.master_id, message=recommend_message, random_id=(r_id + 1))
        return

    def give_today_stats(self):
        """
        Gives today's time with the highest online percent
        :return: nothing
        """
        # Just today's stats

        # con = sql.connect('vk_bot.db')
        # cur = con.cursor()
        name = "stats" + str(self.group_id) + str(self.master_id)

        r_id = func.get_r_id()

        day = datetime.datetime.now().weekday()

        start = day * self.analyses_per_day
        finish = (day + 1) * self.analyses_per_day

        recommend_message = f"Сегодня лучшим для постов временем в группе '{self.name}' было "

        max_online, best_time = 0, 0
        for i in range(start, finish):
            sq = f"SELECT archive4 FROM {name} WHERE analyse_number={i}"
            cur.execute(sq)
            current_percent = cur.fetchone()[0]
            if current_percent > max_online:
                max_online = current_percent
                best_time = i

        sq = f"SELECT time FROM {name} WHERE analyse_number={best_time}"
        cur.execute(sq)
        recommend_time = cur.fetchone()[0]
        recommend_message += recommend_time[5:] + ": " + str(max_online) + "%"
        vk_api2.messages.send(user_id=self.master_id, message=recommend_message, random_id=r_id)
        return

    def give_this_week_stats(self):
        """
        does the same as the 'recommendation_for_this_week' but can be summoned by the user every moment. It also take
        certain percents of the current week, not average
        :return: nothing
        """
        # Just this week stats

        # con = sql.connect('vk_bot.db')
        # cur = con.cursor()
        name = "stats" + str(self.group_id) + str(self.master_id)

        r_id = func.get_r_id()
        recommend_message = f"На этой неделе лучшим для постов в группе '{self.name}' временем было "
        max_online, best_time, max_summary_during_the_day, best_day = 0, 0, 0, 0

        for j in range(7):
            max_summary_during_the_day, best_day, best_time, max_online = \
                self.get_one_day_information_v2(j, max_summary_during_the_day, best_day, best_time, max_online)
        max_average_during_the_day = max_summary_during_the_day // self.analyses_per_day + 1

        sq = f"SELECT time FROM {name} WHERE analyse_number={best_time}"
        cur.execute(sq)
        recommend_time = cur.fetchone()[0]
        recommend_message += recommend_time + ": " + str(max_online) + "%"
        vk_api2.messages.send(user_id=self.master_id, message=recommend_message, random_id=r_id)

        recommend_message = "This week, the day with the biggest average online percent was " + \
                            days_of_the_week[best_day] + ": " + str(max_average_during_the_day) + "%"
        vk_api2.messages.send(user_id=self.master_id, message=recommend_message, random_id=(r_id + 1))
        return

    def work_and_print(self):
        """
        updates data and sends current online percent
        :return:
        """
        r_id = func.get_r_id()

        week_day = datetime.datetime.now().weekday()
        t = datetime.datetime.now()

        array_cell = week_day * self.analyses_per_day + (t.hour * 60 + t.minute) // self.period
        percent = self.group_analyse()

        self.update_data(percent, array_cell)

        if self.current_percents:
            string = f"В группе '{self.name}' сейчас онлайн {str(percent)}% участников"
            vk_api2.messages.send(user_id=self.master_id, message=string, random_id=r_id)
        return

    def calculate_new_analyse_time(self):
        """
        This function runs in the very beginning. It counts when to start analysing and when to give recommendations
        """
        r_id = func.get_r_id()
        current_time = datetime.datetime.now().replace(second=0, microsecond=0)
        current_minutes = current_time.minute + current_time.hour * 60
        minutes_to_wait = self.period - current_minutes % self.period
        next_analyse_time = current_time + datetime.timedelta(0, 0, 0, minutes_to_wait // 60, minutes_to_wait % 60, 0,
                                                              0)
        next_recommend_time = current_time.replace(microsecond=0, second=0, minute=0, hour=0) + datetime.timedelta(
            days=1
        )
        ok_message = f"Йес, май диар! Обработка '{self.name}' начата, результат через {minutes_to_wait} минут!"
        vk_api2.messages.send(user_id=self.master_id, message=ok_message, random_id=r_id)
        return next_analyse_time, next_recommend_time
