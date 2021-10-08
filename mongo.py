from config import *
import tweepy
import json
from bson import ObjectId
import certifi
from flask import Flask, render_template,redirect, url_for, flash
from flask import request
from flask_pymongo import PyMongo
import requests


class JSONEncoder(json.JSONEncoder):
  def default(self, o):
    if isinstance(o, ObjectId):
      return str(o)
    return json.JSONEncoder.default(self, o)


app = Flask(__name__)

app.secret_key = "super secret key"
app.config['MONGO_DBNAME'] = 'db'
app.config['MONGO_URI'] = 'mongodb+srv://user:pass1234@cluster0.nmzhw.mongodb.net/db?retryWrites=true&w=majority'

mongo = PyMongo(app,tlsCAFile=certifi.where())

response = requests.get('https://api.twitter.com/2/tweets/search/recent?query=%23covid&max_results=100&tweet.fields=public_metrics',headers=myheaders)

json_res = response.json()
twitterData = json_res['data']
print(twitterData)
records = mongo.db.collection
fb_rec = mongo.db.fb_collection
#records.insert_many(y)
#print(records)

x=[]
y={}
@app.route('/', methods=['GET'])
def home():
  #todos = mongo.db.collection
  #for doc in todos.find():
   # x.append(doc)
   # y = JSONEncoder().encode(x)
  #jsonify(y)
  return render_template("home.html")

@app.route('/tweet', methods=['GET'])
def tweet():
  return render_template('tweet.html')

@app.route('/twiiter', methods=['POST'])
def twitter():
  if request.method == 'POST':
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    tweet = request.form['tweet']
    post= api.update_status(tweet)
    #print(post)
    records.insert_one({
      'id':post.id_str,
      'public_metrics':{
      "retweet_count":post.retweet_count,
      "like_count":post.favorite_count,
      "quote_count":post.is_quote_status,

    },
      'text':post.text
    })
    flash("Posted on twitter")

    return redirect(url_for('tweet'))

@app.route('/fbpost',methods=['POST','GET'])
def fbpost():
  if request.method=='GET':
    return render_template('fbpost.html')
  elif request.method=='POST':
    fb_post= request.form['fb']
    pay = {
      'message':fb_post,
      'access_token':fb_access_token
    }
    res= requests.post('https://graph.facebook.com/112620424521351/feed',params=pay)
    res_id = res.json()
    print(res_id)
    print(res_id['id'])
    post_id = str(res_id['id'])
    print(type(post_id))

    post_mongo = requests.get('https://graph.facebook.com/v12.0/'+str(post_id),params={'access_token':fb_access_token, 'fields':'id,created_time,message,from,status_type,instagram_eligibility'})
    mongo_data_fb= post_mongo.json()
    print(mongo_data_fb['id'])
    fb_rec.insert_one({
      'id':mongo_data_fb['id'],
      'instagram_eligibility':mongo_data_fb['instagram_eligibility'],
      'message':mongo_data_fb['message'],
      'status_type':mongo_data_fb['status_type'],
      'created_time':mongo_data_fb['created_time'],
      'from':{
        'name':mongo_data_fb['from']['name'],
        'id':mongo_data_fb['from']['id']
      },
    })
    flash("Posted on facebook")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)