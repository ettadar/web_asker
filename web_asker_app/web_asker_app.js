Questions = new Mongo.Collection("questions")

if (Meteor.isClient) {
  Template.body.helpers({
    questions : function () {
      return Questions.find({}, {sort: {priority: -1}});
    }
  });

  Template.question.events({
    "click .answer": function () {
      Questions.update(Template.parentData(0)._id, {$set: {answer: this.text}})
    }
  });

  Template.vis.rendered = function () {
    var svg, width = 550, height = 75, x;

    svg = d3.select('#circles').append('svg')
      .attr('width', width)
      .attr('height', height);

    var drawCircles = function () {
      var data = Template.parentData(0).data;
      var circles = svg.selectAll('circle').data(data);
      circles = circles.enter().append('circle')
        .attr('cx', function (d, i) { return x(i); })
        .attr('cy', height / 2);
      circles.attr('r', function (d) { return d; });
    };

    var updateCircles = function (id) {
      var data = Questions.findOne(id).data;
      console.log(data)
      var circles = svg.selectAll('circle').data(data);
      circles = circles.transition().duration(500);
      circles.attr('r', function (d) { return d; });
    }

    var id = Template.parentData(0)._id
    Questions.find(Template.parentData(0)._id).observe({
      added: function () {
        x = d3.scale.ordinal()
          .domain(d3.range(Template.parentData(0).data.length))
          .rangePoints([0, width], 1);
        drawCircles();
      },
      changed: function () {console.log(id); updateCircles(id)}
    });
  };
}