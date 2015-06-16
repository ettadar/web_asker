import subprocess
import os
import time

from pymongo import MongoClient

class WebAsker(object):
    def __init__(self, mongo_db_adress):
        client = MongoClient(mongo_db_adress)

        self._candidates_col = client["meteor"]["candidates"]
        self._answer_col = client["meteor"]["answer"]
        self._question_col = client["meteor"]["question"]

        self._is_question_asked = False

    def is_answer_ready(self):
        return len(list(self._answer_col.find())) == 1

    def get_answer(self):
        if self._is_question_asked:
            while True:
                answer_list = list(self._answer_col.find())
                if (len(answer_list)):
                    self._question_col.remove()
                    self._candidates_col.remove()
                    self._answer_col.remove()

                    self._is_question_asked = False

                    return answer_list[0]["text"]
                time.sleep(0.1)

        else:
            return None

    def ask(self, question, answer_list):
        self._question_col.remove()
        self._candidates_col.remove()
        self._answer_col.remove()

        self._question_col.insert({"text" : question})
        self._candidates_col.insert([{"text" : a} for a in answer_list])

        self._is_question_asked = True
