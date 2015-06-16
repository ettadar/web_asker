from web_asker import WebAsker

if __name__ == '__main__':
    import time
    wa = WebAsker("mongodb://127.0.0.1:3001/meteor")
    wa.ask("Question 1 ?", ["yes", "no"])
    print wa.get_answer()

    t = 0
    last_t = 0
    while True:
        if t - last_t > 5:
            last_t = t
            wa.ask("Question {} ?".format(t / 5), ["yes", "no"])
            print "ask"
        if wa.is_answer_ready():
            print wa.get_answer()
        time.sleep(0.1)
        t += 0.1
    

