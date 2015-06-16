Candidates = new Mongo.Collection("candidates");
Answer = new Mongo.Collection("answer");
Question = new Mongo.Collection("question")

Meteor.methods({
  selectAnswer: function (text) {
    Candidates.remove({});
    Question.remove({});

    Answer.insert({"text" : text});
  },
});

if (Meteor.isClient) {
  Template.body.helpers({
    candidates : function () {
      return Candidates.find();
    }
  });

  Template.question.helpers({
    name : function () {
        return Question.findOne()["text"];
    },
  });


  Template.candidate.events({
    "click .action": function () {
      var text = this.text;
      Meteor.call("selectAnswer", text)
    }
  });
}