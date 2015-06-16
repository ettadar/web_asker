from web_asker import WebAsker

if __name__ == '__main__':
    import time
    web_asker = WebAsker("mongodb://127.0.0.1:3001/meteor")
    web_asker.clear_all()

    question = web_asker.ask("Question 1 ?", ["yes", "no"])
    print question.get_answer()


    t = 0
    last_t = 0

    question = web_asker.ask("Question {} ?".format(t / 5), ["yes", "no"])
    answer = None
    while True:
        if answer is None and question.answered():
            answer = question.get_answer()
            print answer

        if t - last_t > 5:
            last_t = t
            
            question.remove()
            answer = None

            question = web_asker.ask("Question {} ?".format(t / 5), ["yes", "no"])
            
            print "ask"

        time.sleep(0.1)
        t += 0.1
    

