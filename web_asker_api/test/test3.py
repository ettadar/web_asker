import time
import json
import numpy as np

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

    t = 0
    last_t = 0
    window = 1
    period = 0.05

    answer_counter_list = np.array([0] * 3)

    pause_question = web_asker.ask("Pause ?", ["Pause !"], priority=10)
    feedback_question = web_asker.ask("Rate behavior : ", [])

    plot = web_asker.plot(answer_counter_list, priority=20)

    while True:
        if pause_question.answered():
            feedback_question.remove()        
            pause_question.remove()
            
            web_asker.ask("Restart ?", ["Restart !"], priority=10).get_answer()

            pause_question = web_asker.ask("Pause ?", ["Pause !"], priority=10)

        if t - last_t > window:
            if not feedback_question.answered():
                feedback_question.remove()

            feedback_question = web_asker.ask("Rate behavior from {}s to {}s :".format(last_t, last_t + window),
                ["0", "1", "2"])

            last_t = int(t)

        time.sleep(period)
        t += period

        if feedback_question.answered():
            answer = int(feedback_question.get_answer())
            print "from {}s to {}s : ".format(last_t - window, last_t), answer
            answer_counter_list[answer] += 1
            plot.update(answer_counter_list * 20 / np.sum(answer_counter_list))

