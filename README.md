Web Asker for vocal Interaction
=========

Web Asker is a tool to ask question. It is composed of two parts : a web app that display question and record answer and a python api to ask question and treat answer. It is design for user studies in a robotic context where:
 - Questions can be blocking or not
 - Question can have a limited lifespan

Web_asker is based on meteor for the web app part and the python api directly talk with the MongoDB database. Since the API require an access to mongoDB you need to install the app on your own server

Installation
------------

To deploy the meteor app on your server follow this tutorial : https://gentlenode.com/journal/meteor-1-deploy-and-manage-a-meteor-application-on-ubuntu-with-nginx/1

In order to have correct performance you also need to setup oplog : https://gentlenode.com/journal/meteor-10-set-up-oplog-tailing-on-ubuntu/17

To install the python API execute :
```
> cd <repo_dir>/web_asker_app
> python setup.py install
```
