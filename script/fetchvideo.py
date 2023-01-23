import threading
import os,time,json
import datetime
from turtle import title
from googleapiclient.discovery import build
import mysql.connector

with open("./script/config.json",'a') as f :     #loading variables from config.json
    data=json.loads(f)

J=1                                         # number of api tokens exhausted
WAIT_TIME=10                                # wait time between two youtube api calls
QUERY="CRICKET"                             # query
PAGES_MAX=5
API_TOKN=data["API_TOKN_1"]
CLIENT_ID=data["CLIENT_ID"]
CLIENT_PWD=data["CLIENT_PWD"]
MYSQL_HOST =data["MYSQL_HOST"]
MYSQL_USER= data["MYSQL_USER"]
MYSQL_PASSWORD= data["MYSQL_PASSWORD"]
MYSQL_DB = data["MYSQL_DB"] 
MAXRESULTS=20                              # number of results in a page

dataBase = mysql.connector.connect(host =MYSQL_HOST,user =MYSQL_USER,passwd =MYSQL_PASSWORD,database=MYSQL_DB) 
lock=threading.Lock()

def heal(e):
    if e=="MySQL Connection not available." :
        dataBase = mysql.connector.connect(host =MYSQL_HOST,user =MYSQL_USER,passwd =MYSQL_PASSWORD,database=MYSQL_DB) 
    if e=="Quota Limit Exceeded":
        J=J+1
        key="API_TOKN_{}".format(J)
        try :
            API_TOKN=data[key]
        except Exception as e:
            print("key exhausted")
class DatabaseOp :
    """
    this class basically does the pushes the entries into the database
    """
    def __init__(self):
        try :
            lock.acquire()
            self.cursorObject=dataBase.cursor()
            self.videos_record = """CREATE TABLE VIDEOS (
                    TAG VARCHAR(100) NOT NULL,
                    TITLE  VARCHAR(500) NOT NULL,
                    DESCRIPTION VARCHAR(500),
                    PUB_TIME VARCHAR(100),
                    THUMB_URLS VARCHAR(200),
                    CHANNELNAME VARCHAR(200)
                    )"""
            self.cursorObject.execute(self.videos_record)    #creating the table for the start
            lock.release()
        except Exception as e :
            heal(e)
            lock.release()
            print("database already created")            #if the table is alrady created it will throw error                     

    def put_data(self,tag,title,description,pub_time,urls,channeltitle) :
        # function to push entries to the table
        #print(tag,title,description,pub_time,urls,channeltitle)
        try :
            print("cursor created")
            query="INSERT INTO VID2 (TAG,TITLE,DESCRIPTION,PUB_TIME,THUMB_URLS,CHANNELNAME) VALUES (%s,%s,%s,%s,%s,%s)"
            val = (tag,title, description, pub_time, urls, channeltitle)
            print("locking")
            lock.acquire()
            cursorObject = dataBase.cursor()
            cursorObject.execute(query, val)
            dataBase.commit()
            lock.release()
            print("releasing lock 1")
        except Exception as e :
            lock.release()
            print("releasing lock 2")
            heal(e)
            print("error while inserting entry",tag,title,description,pub_time,urls,channeltitle)
            print(e)
        

class DataOp :
    """
    This class basically take the fetched json data, traverses over the entries and pushes them parallely using threading
    """
    def __init__(self):
        print("DataOp initiated")
        pass

    def data_operation(self,response,DatabaseOp):
        try :
            no_threads= 5                              #size of thread pool
            no_threads=min(no_threads,response["pageInfo"]["resultsPerPage"])   
            i=0
            threads=[]                                  #thread pool
            for item in response["items"] :
                tag=item["etag"]
                pub_time=item["snippet"]["publishedAt"]
                description=item["snippet"]["description"]
                urls=item["snippet"]["thumbnails"]["high"]["url"]
                title=item["snippet"]["title"]
                channeltitle=item["snippet"]["channelTitle"]
                i=i+1
                print("starting thread")
                t=threading.Thread(target=DatabaseOp.put_data,args=[tag,title,description,pub_time,urls,channeltitle])
                t.start()
                threads.append(t)
                if i==no_threads :                     # when size of thread pool is full
                    for thread in threads :
                        thread.join()                  # waiting for all threads to execute in thread pool
                    i=0
                    threads=[]                         # hence emptying the thread pool
            return 
        except Exception as e :
            heal(e)
            print("expected error occured : ",e)
            

            



class SearchVideosYoutube :
    """
    This class basically uses the youtube api call to fetch the info for the query
    """
    def __init__(self):
        self.youtube=build('youtube','v3',developerKey=API_TOKN)
        self.db_op=DatabaseOp()
        self.dataop=DataOp()

    def search_videos_since(self,tm) :
        request=self.youtube.search().list(part="id,snippet",type='video',q=QUERY,videoDuration='short',videoDefinition='high',maxResults=MAXRESULTS,publishedAfter=tm)
        response = request.execute()
        self.dataop.data_operation(response,self.db_op)
        while(response.get("nextPageToken")) :
            request=self.youtube.search().list(part="id,snippet",type='video',q=QUERY,videoDuration='short',videoDefinition='high',maxResults=MAXRESULTS,publishedAfter=tm,pageToken=response["nextPageToken"])
            response = request.execute()
            self.dataop.data_operation(response,self.db_op)

    def search_videos(self) :
        request=self.youtube.search().list(part="id,snippet",type='video',q=QUERY,videoDuration='short',videoDefinition='high',maxResults=MAXRESULTS)
        response = request.execute()
        #print(response)
        self.dataop.data_operation(response,self.db_op)
        for i in range(0,PAGES_MAX):
            request=self.youtube.search().list(part="id,snippet",type='video',q=QUERY,videoDuration='short',videoDefinition='high',maxResults=MAXRESULTS,pageToken=response["nextPageToken"])
            response = request.execute()
            self.dataop.data_operation(response,self.db_op)
    
    
    def startcalls(self):
        request = self.search_videos()
        n = datetime.datetime.now(datetime.timezone.utc)
        n=n.isoformat()
        while(1) :
            print("sleeping.......................")
            time.sleep(WAIT_TIME)
            request = self.search_videos_since(n)
            n = datetime.datetime.now(datetime.timezone.utc)
            n=n.isoformat()


            


if __name__ == '__main__':
    search_video=SearchVideosYoutube()
    search_video.startcalls()
