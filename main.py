from flask import Flask, request, jsonify, redirect, url_for,render_template
from flask_restful import Resource, Api
import hvac,os,json
import sys, jwt, yaml
import mysql.connector
from flask_cors import CORS
from functools import wraps
app = Flask(__name__)
api = Api(app)
CORS(app, resources={r'/*': {'origins': '*'}})
MYSQL_HOST = "127.0.0.1"
MYSQL_USER= "root"
MYSQL_PASSWORD= "mariadb"
MYSQL_DB = "start"

class DBOps :
    def __init__(self):
        self.dataBase = mysql.connector.connect(host =MYSQL_HOST,user =MYSQL_USER,passwd =MYSQL_PASSWORD,database=MYSQL_DB)
    
    def get_video_title(self,title) :
        query="SELECT * FROM VID2 where TITLE='{}'".format(title)
        create_cursor = self.dataBase.cursor()
        create_cursor.execute(query)
        response=[]
        for x in create_cursor:
            print(x[0])
            response.append({"tag":x[0],"title":x[1],"DESCRIPTION":x[2],"UploadTime":x[3],"ThumbnailUrl":x[4],"ChannelName":x[5]})
        
        return response

    def get_video_description(self,description) :
        query="SELECT * FROM VID2 where DESCRIPTION='{}'".format(description)
        create_cursor = self.dataBase.cursor()
        create_cursor.execute(query)
        response=[]
        for x in create_cursor:
            response.append({"tag":x[0],"title":x[1],"DESCRIPTION":x[2],"UploadTime":x[3],"ThumbnailUrl":x[4],"ChannelName":x[5]})
        
        return response

db_operations=DBOps()

class SearchVideo(Resource) :
    def get(self):
        data=request.headers
        content_type = data.get('Content-Type')
        if (content_type == 'application/json'):
            try :
                title=request.headers['title']
                return db_operations.get_video_title(title)
            except Exception as e:
                description=request.headers['description']
                return db_operations.get_video_description(description)


api.add_resource(SearchVideo,"/api/v1/search")

if __name__ == '__main__':
    app.run()