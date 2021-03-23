from flask import Flask, render_template, request, redirect, url_for
import os
import pymongo
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

MONGO_URI = os.environ.get('MONGO_URI')
DB_NAME = 'sample_restaurants'

client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]

@app.route('/')
def home():
    return render_template('home.template.html')

@app.route('/results')
def show_results():
    return render_template('results.template.html')


# "magic code" -- boilerplate
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)