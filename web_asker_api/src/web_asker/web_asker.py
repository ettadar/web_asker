from kinect2.client import Kinect2Client
from pymongo import MongoClient
from os import path
from web_asker import __file__ as filename
import time
import json


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
        mapped_speech = self._asker.mapped_speech
        for candidate_answer, key in mapped_speech:
            if candidate_answer in self._asker.answers_dict[self._mogo_db_id]:
                self.answer = candidate_answer
                answered_from_voice = True
                del self._asker.stamped_speech[key]
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
                print("Answer taken into account: '{}'".format(answer))
                return answer
            time.sleep(0.02)

    def remove(self):
        self._asker.questions_col.remove({"_id": self._mogo_db_id})
        del self._asker.answers_dict[self._mogo_db_id]


class WebAsker(object):
    def __init__(self, mongo_db_adress):
        client = MongoClient(mongo_db_adress)
        db_name = mongo_db_adress.split("/")[-1]
        self._mogo_db_id = None
        self.questions_col = client[db_name]["questions"]
        self.answers_dict = {}
        self.stamped_speech = {}
        print("Connecting to the Kinect server...")
        self.client = Kinect2Client("BAXTERFLOWERS.local")
        self.client.tts.params.set_language('english')
        with open(path.join(path.dirname(filename), '..', 'config', 'grammar_toolbox.xml')) as f:
            self.action_grammar = f.read()
        with open(path.join(path.dirname(filename), '..', 'config', 'speech_mapping.json')) as f:
            self.mapping = json.load(f)
        self.client.speech.params.set_grammar(self.action_grammar)
        self.client.speech.params.use_system_mic()
        self.client.speech.params.set_confidence(0.3)
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
        if "wanted" in string:
            string = "Should I do one of these options"
        return string.lower()

    @property
    def all_speech(self):
        # Delete speech older than 1 second ago
        to_delete = []
        for answer, timestamp in self.stamped_speech.iteritems():
            if time.time() - timestamp > 1.:
                to_delete.append(answer)
        for answer in to_delete:
            del self.stamped_speech[answer]

        return self.stamped_speech.keys()

    @property
    def mapped_speech(self):
        speech = []
        for answer in self.all_speech:
            if answer in self.mapping:
                command = self.mapping[answer]
            else:
                splitted_answer = answer.split(' ')
                command = splitted_answer[0] + '(' + ', '.join(splitted_answer[1:]) + ')'
            speech.append((command, answer))
        return speech

    def ask(self, question, answer_list, priority=0, auto_remove=True, color="grey"):
        #print question, color
        self.client.tts.say(self.clean(question), blocking=False)
        question_id = self.questions_col.insert({
            "text": question,
            "answer_candidates": [{"text": a} for a in answer_list],
            "priority": priority,
            "color": color
        })
        self.answers_dict.update({question_id: answer_list})
        return WebQuestion(question_id, self, auto_remove)

    def cb_speech_received(self, speech):
        key = ' '.join([word for word in speech['semantics'] if word != ''])
        self.stamped_speech[key] = time.time()

    def clear_all(self):
        self.questions_col.remove()
        self.answers_dict = {}
