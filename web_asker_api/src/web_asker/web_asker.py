from kinect2.client import Kinect2Client
from pymongo import MongoClient
import time

class WebQuestion(object):
    def __init__(self, mongo_db_id, asker, auto_remove):
        self._mogo_db_id = mongo_db_id
        self._asker = asker
        self._auto_remove = auto_remove
        self.answer = ""

    def answered(self):
        answered_from_gui = self._asker.questions_col.find_one({
                                "answer": {"$exists": True}, "_id": self._mogo_db_id}) is not None
        
        answered_from_voice = False
        self.answer = ""
        for answer, full_answer in self._asker.answers_dict[self._mogo_db_id]:  # example: "do it", "Do It!"
            if self._asker.all_speech.count(answer) > 0:
                self.answer = full_answer
                answered_from_voice = True
                break

        return answered_from_gui or answered_from_voice

    def get_answer(self):
        while True:
            answer = self.answer
            # GUI
            result = self._asker.questions_col.find_one({
                "answer": {"$exists": True}, "_id": self._mogo_db_id})
            if result is not None:
                answer = result["answer"]  # Override speech

            if answer != "":
                if self._auto_remove:
                    self.remove()
                    self.answer = ""
                print("Answer taken into account: '{}'".format(self.answer))
                return answer
            time.sleep(0.1)

    def remove(self):
        self._asker.questions_col.remove({"_id": self._mogo_db_id})
        del self._asker.answers_dict[self._mogo_db_id]
        self._asker.update_vocabulary()


class WebAsker(object):
    def __init__(self, mongo_db_adress):
        client = MongoClient(mongo_db_adress)
        db_name = mongo_db_adress.split("/")[-1]
        self._mogo_db_id = None
        self.questions_col = client[db_name]["questions"]
        self.answers_dict = {}
        self.all_speech = []
        print("Connecting to the Kinect server...")
        self.client = Kinect2Client("BAXTERFLOWERS.local")
        self.client.tts.params.set_language('english')
        self.client.speech.params.set_vocabulary([])
        self.client.speech.set_callback(self.cb_speech_received)
        self.client.speech.start()
        self.client.tts.start()
        print("Kinect connected!")

    @staticmethod
    def clean(string):
        string = string.replace('start_', '')
        string = string.replace('/toolbox/', '')
        string = string.replace('(', ' ')
        string = string.replace('_', ' ')
        string = string.replace('/', ' ')
        string = string.replace(')', '')
        string = string.replace('?', '')
        string = string.replace('!', '')
        return string.lower()

    def ask(self, question, answer_list, priority=0, auto_remove=True, color="grey"):
        #print question, color
        self.client.tts.say(self.clean(question), blocking=False)
        question_id = self.questions_col.insert({
            "text": question,
            "answer_candidates": [{"text": a} for a in answer_list],
            "priority": priority,
            "color": color
        })
        question_answers = [(self.clean(answer), answer) for answer in answer_list]
        self.answers_dict.update({question_id: question_answers})
        self.update_vocabulary()
        return WebQuestion(question_id, self, auto_remove)

    def cb_speech_received(self, speech):
        self.all_speech.append(speech['semantics'][0])  # TODO locking  # TODO kinect_2_server: dictionary of lists???

    @property
    def all_answers_of_all_questions(self):
        return [answer[0] for answers in self.answers_dict.values() for answer in answers]

    def update_vocabulary(self):
        print("You can say: {}".format(self.all_answers_of_all_questions))
        self.client.speech.params.set_vocabulary(self.all_answers_of_all_questions, language='en-US')
        self.client.speech.params.send_params()

    def clear_all(self):
        self.questions_col.remove()
        self.client.speech.params.set_vocabulary([])
        self.client.speech.params.send_params()
