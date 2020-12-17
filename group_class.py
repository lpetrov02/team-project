import vk
import datetime
import requests
import time
import random
import analyse_and_bot_functions as func
import math


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
        self.period = freq
        self.analyses_per_day = 1440 // self.period
        analyses_per_week = self.analyses_per_day * 7
        self.average_percents = [0 for i in range(analyses_per_week)]
        self.archive = [[0, 0, 0, 0] for i in range(analyses_per_week)]
        self.number = [0 for i in range(analyses_per_week)]
        self.index_to_date = []

    def fill_in_index_to_date(self):
        # index_to_date is the array that gives you certain time 
        for i in range(self.analyses_per_day):
            time_index = i % self.analyses_per_day * self.period
            hour_index = time_index // 60
            minute_index = time_index % 60
            s = ", " 
            if hour_index == 0:
                s += '0'
            s += str(hour_index) + ":" + str(minute_index)
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
        if self.number[cell_to_update] >= 4:
            self.average_percents[cell_to_update] *= 4
            self.average_percents[cell_to_update] = self.average_percents[cell_to_update] - \
                                                    self.archive[cell_to_update][0] + new_one
            self.average_percents[cell_to_update] /= 4
        else:
            self.average_percents[cell_to_update] *= self.number[cell_to_update]
            self.average_percents[cell_to_update] = self.average_percents[cell_to_update] + new_one
            self.number[cell_to_update] += 1
            self.average_percents[cell_to_update] /= self.number[cell_to_update]
        for j in range(3):
            self.archive[cell_to_update][j] = self.archive[cell_to_update][j + 1]
        self.archive[cell_to_update][3] = new_one

    def recommendation_for_this_day_of_the_week(self):
        """
        this function runs at about 00:00 daily and recommends: when it is going to be the best time for posts this day.
        :return: returns nothing, just sends a message with recommendation
        """
        # average stats and recommendation for this day of the week past 4 last weeks
        r_id = func.get_r_id(self.master_id)
        
        day = datetime.datetime.now().weekday()
        start = day * self.analyses_per_day
        finish = (day + 1) * self.analyses_per_day
        
        recommend_message = "Possibly, today the best time will be "
        max_online, best_time = 0, 0
        for i in range(start, finish):
            if self.average_percents[i] > max_online:
                max_online = self.average_percents[i]
                best_time = i

        best_time %= self.analyses_per_day
        recommend_message += days_of_the_week[day] + self.index_to_date[best_time] + ": " + str(max_online) + "%"
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
        summary_percents = 0
        for i in range(self.analyses_per_day * day, self.analyses_per_day * (day + 1)):
            summary_percents += self.average_percents[i]
            if self.average_percents[i] > max_online:
                max_online = self.average_percents[i]
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
        summary_percents = 0
        for i in range(self.analyses_per_day * day, self.analyses_per_day * (day + 1)):
            summary_percents += self.arcive[i][3]
            if self.archive[i][3] > max_online:
                max_online = self.archive[i][3]
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
        r_id = func.get_r_id(self.master_id)
        recommend_message = "Possibly, this week the best time will be "
        max_online, best_time, max_summary_during_the_day, best_day = 0, 0, 0, 0

        for j in range(7):
            max_summary_during_the_day, best_day, best_time, max_online = \
                self.get_one_day_information_v1(j, max_summary_during_the_day, best_day, best_time, max_online)
        max_average_during_the_day = max_summary_during_the_day / self.analyses_per_day

        day_with_the_best_time = best_time // self.analyses_per_day
        best_time %= self.analyses_per_day
        recommend_message += days_of_the_week[day_with_the_best_time] + \
                             self.index_to_date[best_time] + ": " + str(max_online) + "%"
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
        r_id = func.get_r_id(self.master_id)

        day = datetime.datetime.now().weekday()
        start = day * self.analyses_per_day
        finish = (day + 1) * self.analyses_per_day

        recommend_message = "Today the best time was "

        max_online, best_time = 0, 0
        for i in range(start, finish):
            if self.archive[i][3] > max_online:
                max_online = self.archive[i][3]
                best_time = i

        best_time %= self.analyses_per_day
        recommend_message += self.index_to_date[best_time] + ": " + str(max_online) + "%"
        vk_api2.messages.send(user_id=self.master_id, message=recommend_message, random_id=r_id)
        return

    def give_this_week_stats(self):
        """
        does the same as the 'recommendation_for_this_week' but can be summoned by the user every moment. It also take
        certain percents of the current week, not average
        :return: nothing
        """
        # Just this week stats
        r_id = func.get_r_id(self.master_id)
        recommend_message = "This week the best time was "
        max_online, best_time, max_summary_during_the_day, best_day = 0, 0, 0, 0

        for j in range(7):
            max_summary_during_the_day, best_day, best_time, max_online = \
                self.get_one_day_information_v2(j, max_summary_during_the_day, best_day, best_time, max_online)
        max_average_during_the_day = max_summary_during_the_day / self.analyses_per_day

        best_time %= self.analyses_per_day
        day_with_the_best_time = best_time // self.analyses_per_day
        recommend_message += days_of_the_week[day_with_the_best_time] + \
                             self.index_to_date[best_time] + ": " + str(max_online) + "%"
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
        r_id = func.get_r_id(self.master_id)
        
        week_day = datetime.datetime.now().weekday()
        t = datetime.datetime.now()
        
        array_cell = week_day * self.analyses_per_day + (t.hour * 60 + t.minute) // self.period
        percent = self.group_analyse()
        
        self.update_data(percent, array_cell)
        
        string = "Online percent in " + self.group_id + " is " + str(percent) + "%"
        vk_api2.messages.send(user_id=self.master_id, message=string, random_id=r_id)
        return

    def analyse(self, next_time):
        """
        :param: next_time - when to analyse again
        :return:
        """
        next_time += datetime.timedelta(hours=(self.period // 60), minutes=(self.period % 60))
        self.work_and_print()
        return next_time

    def calculate_new_analyse_time(self):
        """
        This function runs in the very beginning. It counts when to start analysing and when to give recommendations
        """
        r_id = func.get_r_id(self.master_id)
        current_time = datetime.datetime.now().replace(second=0, microsecond=0)
        current_minutes = current_time.minute + current_time.hour * 60
        minutes_to_wait = self.period - current_minutes % self.period
        next_analyse_time = current_time + datetime.timedelta(0, 0, 0, minutes_to_wait // 60, minutes_to_wait % 60, 0, 0)
        next_recommend_time = current_time.replace(microsecond=0, second=0, minute=0, hour=0) + datetime.timedelta(
            days=1
        )
        ok_message = "OK! Starting in " + str(minutes_to_wait) + " minutes!"
        vk_api2.messages.send(user_id=self.master_id, message=ok_message, random_id=r_id)
        return next_analyse_time, next_recommend_time
