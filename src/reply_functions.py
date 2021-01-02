import vk
import random
import json
import src.analyze_functions as func

# top-secret information
group_token = "17e681fbe171945431a04f1abc752d41ff888698288abf74124de4e782c67f36e76484601991870f56b7a"

session2 = vk.AuthSession(access_token=group_token)
vk_api2 = vk.API(session2, v=5.92)


def incorrect_id(current_user_id):
    # informs about the mistake in group id
    r_id = func.get_new_random_id()
    vk_api2.messages.send(
        user_id=current_user_id, message="Ummmm... Something went wrong! Incorrect group id!", random_id=r_id
    )
    return


def incorrect_period_value(current_user_id):
    # informs about the mistake in a period value
    r_id = func.get_new_random_id()
    s = "Bro, listen here! If your period is less than an hour, in should divide 60. And anyway, it should divide 1440)"
    vk_api2.messages.send(user_id=current_user_id, message=s, random_id=r_id)
    return


def say_hello(current_user_id):
    # sends a message 'Ну привет, ....'
    r_id = func.get_new_random_id()
    greetings = [
        "Ну привет, ", "Здарова бандит-", "Hi, bro ", "Здрасьте. Кто тут лох? Ага - ", "Приветики, ты просто космос, "
    ]
    index = random.randint(0, 4)
    string = greetings[index]
    value = vk_api2.users.get(user_ids=current_user_id, fields='first_name')
    string += value[0]['first_name']
    vk_api2.messages.send(user_id=current_user_id, message=string, random_id=r_id)
    return


def instruction_message(current_user_id):
    # sends the message if user did send us the message of an unknown format
    r_id = func.get_new_random_id()
    string = "Maaaaaaan! I don't understand you... Read the instruction please. If you need it in a bigger variant"
    string += ", send 'help'"

    vk_api2.messages.send(
        user_id=current_user_id, message=string, attachment="photo-200698416_457239022", random_id=r_id
    )
    return


def not_available(current_user_id):
    r_id = func.get_new_random_id()
    vk_api2.messages.send(user_id=current_user_id, message="Not available now, give a task at first!", random_id=r_id)
    vk_api2.messages.send(user_id=current_user_id, sticker_id=4331, random_id=(r_id + 1))
    return


def not_available_i_am_busy(current_user_id):
    r_id = func.get_new_random_id()
    vk_api2.messages.send(user_id=current_user_id, message="Impossible because... i am busy!", random_id=r_id)
    vk_api2.messages.send(user_id=current_user_id, sticker_id=4331, random_id=(r_id + 1))
    return


def task_by_button(current_user_id):
    # gives the instruction how to give a task
    r_id = func.get_new_random_id()
    vk_api2.messages.send(
        user_id=current_user_id,
        message="Send the id of the group and the period with a whitespace between them and the '$' in the beginning",
        random_id=r_id
    )


def send_big_instruction(current_user_id):
    # sends the instruction for the user
    r_id = func.get_new_random_id()

    kb = \
        {
            "one_time": False,
            "buttons": [
                [
                    {
                        "action": {
                            "type": "text",
                            "payload": "{\"button\": \"1\"}",
                            "label": "Stop"
                        },
                        "color": "negative"
                    },
                    {
                        "action": {
                            "type": "text",
                            "payload": "{\"button\": \"2\"}",
                            "label": "help"
                        },
                        "color": "primary"
                    }
                ],
                [
                    {
                        "action": {
                            "type": "text",
                            "payload": "{\"button\": \"2\"}",
                            "label": "recommend: day"
                        },
                        "color": "secondary"
                    },
                    {
                        "action": {
                            "type": "text",
                            "payload": "{\"button\": \"2\"}",
                            "label": "recommend: week"
                        },
                        "color": "secondary"
                    }
                ],
                [
                    {
                        "action": {
                            "type": "text",
                            "payload": "{\"button\": \"2\"}",
                            "label": "Want to give a task"
                        },
                        "color": "positive"
                    },
                    {
                        "action": {
                            "type": "text",
                            "payload": "{\"button\": \"2\"}",
                            "label": "Set time"
                        },
                        "color": "primary"
                    }
                ]
            ]
        }

    kb = json.dumps(kb, ensure_ascii=False).encode('utf-8')
    kb = str(kb.decode('utf-8'))

    vk_api2.messages.send(
        user_id=current_user_id,
        message="В рамочку и на стену",
        attachment="photo-200698416_457239023",
        random_id=r_id,
        keyboard=kb
    )
    return