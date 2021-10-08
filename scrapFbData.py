import requests
import certifi
from pymongo import MongoClient
from config import *


client = MongoClient("mongodb+srv://user:pass14@cluster0.nmzhw.mongodb.net/db?retryWrites=true&w=majority",tlsCAFile=certifi.where())

db = client.get_database('db')
records = db.fb_collection
payload = {'fields': 'id,name,birthday,posts{id,instagram_eligibility,message,shares,status_type,created_time,from}', 'access_token':fb_access_token}

res = requests.get('https://graph.facebook.com/v3.0/me/',params=payload)
resp = res.json()
fb_data = resp['posts']['data']
print(resp['name'])
records.insert_many(fb_data)

