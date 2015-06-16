Questions = new Mongo.Collection("questions")

if (Meteor.isClient) {
  Template.body.helpers({
    questions : function () {
      return Questions.find();
    }
  });

  Template.question.events({
    "click .answer": function () {
      Questions.update(Template.parentData(0)._id, {$set: {answer: this.text}})
    }
  });
}