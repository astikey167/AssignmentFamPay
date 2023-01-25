from flask import Flask, request, jsonify, redirect, url_for,render_template
from flask_restful import Resource, Api
import hvac,os,json
import sys, jwt, yaml
import mysql.connector
from flask_cors import CORS
from functools import wraps
from dateutil import parser
app = Flask(__name__)
api = Api(app)
CORS(app, resources={r'/*': {'origins': '*'}})
with open("./script/config.json",'a') as f :     #loading variables from config.json
    data=json.loads(f)

MYSQL_HOST =data["MYSQL_HOST"]
MYSQL_USER= data["MYSQL_USER"]
MYSQL_PASSWORD= data["MYSQL_PASSWORD"]
MYSQL_DB = data["MYSQL_DB"]

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

    def get_all_data(self):
        query="SELECT * FROM VID2"
        create_cursor = self.dataBase.cursor()
        create_cursor.execute(query)
        response=[]
        for x in create_cursor:
            response.append({"tag":x[0],"title":x[1],"DESCRIPTION":x[2],"UploadTime":x[3],"ThumbnailUrl":x[4],"ChannelName":x[5]})
        
        response.sort(key=lambda val: parser.parse(val["UploadTime"]))
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

class FetchVideo(Resource) :
    def get(self):
        data=request.headers
        content_type = data.get('Content-Type')
        if (content_type == 'application/json'):
            return db_operations.get_all_data()

api.add_resource(SearchVideo,"/api/v1/search")
api.add_resource(FetchVideo,"/api/v1/fetch/all")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001)
