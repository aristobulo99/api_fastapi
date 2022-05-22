#from http import client
from pymongo import MongoClient

#conn = MongoClient()
client = MongoClient('mongodb+srv://aplicacion:123456789ABCD@cluster0.r5vvp.mongodb.net/?retryWrites=true&w=majority')
conn = client


