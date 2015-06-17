import subprocess
import os
import time

from pymongo import MongoClient

class WebQuestion(object):
    def __init__(self, mongo_db_id, questions_col):
        self._mogo_db_id = mongo_db_id
        self._questions_col = questions_col

    def answered(self):
        return self._questions_col.find_one({
            "answer" : {"$exists" : True},"_id" : self._mogo_db_id}) is not None

    def get_answer(self):
        while True:
            result = self._questions_col.find_one({
                "answer" : {"$exists" : True}, "_id" : self._mogo_db_id})
            if result is not None:
                self._alive = False
                return result["answer"]
            time.sleep(0.1)

    def remove(self):
        self._questions_col.remove({"_id" : self._mogo_db_id})

class WebAsker(object):
    def __init__(self, mongo_db_adress):
        client = MongoClient(mongo_db_adress)

        self._questions_col = client["web_asker_db"]["questions"]
        self._mogo_db_id = None

    def ask(self, question, answer_list):
        question_id = self._questions_col.insert({
            "text" : question,
            "answer_candidates" : [{"text" : a} for a in answer_list],
            })
        return WebQuestion(question_id, self._questions_col)

    def clear_all(self):
        self._questions_col.remove()
