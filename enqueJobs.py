import pymongo
from rq import Queue
from worker import conn
import datetime
import pytz
import requests

myclient = pymongo.MongoClient("mongodb://admin1:admin1@ds253891.mlab.com:53891/pioneers_of_interactive_entertainment_nu")
mydb = myclient["pioneers_of_interactive_entertainment_nu"]


def enque_job():
    q = Queue(connection=conn)

    my_jobs_col = mydb["jobs"]
    for job in my_jobs_col.find():
        print(f"\nCURRENT JOB IS: {job}\n")
        q.enqueue(handle_single_job, job)
    #result = q.enqueue(count_words_at_url, 'http://heroku.com')


def handle_single_job(job):

    user_date = job["date"]
    user_time = job["time"]
    message_to_send = job["message"]
    cur_col = job["collection"]

    my_datetime_s = f"{user_date} {user_time}"
    # print(f"my_datetime_s = {my_datetime_s}")
    naive_scheduled = datetime.datetime.strptime(my_datetime_s, "%Y-%m-%d %H:%M")
    # print(f"JOB DATE TIME = {naive_scheduled}")
    print(f"LOCALIZED JOB SCHEDULED = {naive_scheduled}")

    chicago_tz = pytz.timezone("America/Chicago")
    now_time_chicago = datetime.datetime.now(chicago_tz)
    now_time_chicago = now_time_chicago.replace(tzinfo=None)
    print(f"CURRENT CHICAGO TIME = {now_time_chicago}")

    # my_timedelta = now_time_chicago - naive_scheduled
    # print(f"my_timedelta = {my_timedelta}")

    should_execute = naive_scheduled <= now_time_chicago

    print(f"Will Execute?: {should_execute}")
    print()

    if should_execute:
        execute_job(message_to_send, cur_col)
        mydb["jobs"].delete_one(job)


def execute_job(message, collection):
    my_data = {'collectionName': collection,
                "userinput": message
               }
#ADDU USER AUTH

    requests.post('https://autotexter9000.herokuapp.com/sendBulkText', data=my_data, auth=('ryanswei', 'ilovedolphins'))
