from flask import Flask, render_template, request, redirect, url_for, flash
import os
import pymongo
from dotenv import load_dotenv

from bson.objectid import ObjectId

load_dotenv()

app = Flask(__name__)

MONGO_URI = os.environ.get('MONGO_URI')
DB_NAME = 'thr_db'

client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]

@app.route('/')
def home():
    return render_template('home.template.html')

@app.route('/results')
def show_results():
    return render_template('results.template.html')

@app.route('/stall/create')
def show_create_stall():
    return render_template('create_stall.template.html')

@app.route('/stall/create', methods=["POST"])
def process_create_stall():
    stall_name = request.form.get('stall_name')
    grading = request.form.get('grading')
    address = request.form.get('address')
    area = request.form.get('area')
    estate = request.form.get('estate')
    cuisine = request.form.get('cuisine')
    specialty_dish_1 = request.form.get('specialty_dish_1')
    specialty_dish_2 = request.form.get('specialty_dish_2')
    specialty_dish_3 = request.form.get('specialty_dish_3')

    db.foodStalls.insert_one({
        "stall_name": stall_name,
        "grading": grading,
        "address": address,
        "area": area,
        "estate": estate,
        "cuisine": cuisine,
        "specialty_dish_1": specialty_dish_1,
        "specialty_dish_2": specialty_dish_2,
        "specialty_dish_3": specialty_dish_3
    })
    
    return redirect(url_for('show_results'))




# "magic code" -- boilerplate
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)