import time

from pymongo import MongoClient


class WebQuestion(object):
    def __init__(self, mongo_db_id, questions_col, auto_remove):
        self._mogo_db_id = mongo_db_id
        self._questions_col = questions_col
        self._auto_remove = auto_remove

    def answered(self):
        return self._questions_col.find_one({
                "answer": {"$exists": True}, "_id": self._mogo_db_id}) is not None

    def get_answer(self):
        while True:
            result = self._questions_col.find_one({
                "answer": {"$exists": True}, "_id": self._mogo_db_id})
            if result is not None:
                if self._auto_remove:
                    self.remove()
                return result["answer"]
            time.sleep(0.1)

    def remove(self):
        self._questions_col.remove({"_id": self._mogo_db_id})


class WebAsker(object):
    def __init__(self, mongo_db_adress):
        client = MongoClient(mongo_db_adress)

        db_name = mongo_db_adress.split("/")[-1]
        self._questions_col = client[db_name]["questions"]
        self._mogo_db_id = None

    def ask(self, question, answer_list, priority=0, auto_remove=True, color="grey"):
        question_id = self._questions_col.insert({
            "text": question,
            "answer_candidates": [{"text": a} for a in answer_list],
            "priority": priority,
            "color": color
            })
        return WebQuestion(question_id, self._questions_col, auto_remove)

    def clear_all(self):
        self._questions_col.remove()
