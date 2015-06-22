import time
import json

from web_asker import WebAsker

web_asker = None
with open("mongo_adress_list.json") as adress_file:
    adress_list = json.load(adress_file)

for adress in adress_list:
    try:
        web_asker = WebAsker(adress)
    except Exception, e:
        print "Cannot reach {}.".format(adress)
        print "Trying next adress..."
    else:
        break

if web_asker is None:
    print "Cannot reach any adress."
else:
    web_asker.clear_all()

    while True:
        question = web_asker.ask("Pick an action :",
            ["Wait", "Hold", "Pick", "Give", "Go_home"])
        action = question.get_answer().lower()

        if action == "wait":
            action_tuple = action

        elif action == "hold":
            question = web_asker.ask("Pick an object :",
                ["Handle", "Side_left", "Side_right", "Side_front", "Side_back"])
            obj = question.get_answer().lower()

            question = web_asker.ask("Pick a pose :", ["0", "1"])
            pose = int(question.get_answer())

            action_tuple = (action, obj, pose)

        elif action == "pick":
            question = web_asker.ask("Pick an object :", ["Handle", "Side_left", "Side_right", "Side_front", "Side_back"], auto_remove=True)
            obj = question.get_answer().lower()

            action_tuple = (action, obj)

        elif action == "give":
            action_tuple = action

        elif action == "go_home":
            question = web_asker.ask("Pick an arm :", ["Left", "Right"])
            arm = question.get_answer().lower()

            action_tuple = (action, arm)


        last_action_text = web_asker.ask("You just picked : " + str(action_tuple), [])
        print action_tuple

        time.sleep(2)
        last_action_text.remove()