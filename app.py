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


# Home page
@app.route('/')
def home():
    return render_template('home.template.html')


# Create stall
# Show form to create stall
@app.route('/stall/create')
def show_create_stall():
    return render_template('create_stall.template.html')

# Process form to create stall
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
        "stall_name": stall_name.lower(),
        "grading": grading.lower(),
        "address": address.lower(),
        "area": area.lower(),
        "estate": estate.lower(),
        "cuisine": cuisine.lower(),
        "specialty_dish_1": specialty_dish_1.lower(),
        "specialty_dish_2": specialty_dish_2.lower(),
        "specialty_dish_3": specialty_dish_3.lower()
    })

    return redirect(url_for('show_create_stall'))


# Show all stalls
@app.route('/stall/results')
def show_all_stalls():
    all_stalls = db.foodStalls.find()
    # find_stall_name = str(request.args.get('find_stall_name'))

    # criteria = {}

    # if find_stall_name:

    #     criteria['stall_name'] = {'$regex': find_stall_name, '$options': 'i'}

    #     all_stalls = db.foodStalls.find(criteria, {
    #         'stall_name': 1,
    #         'area': 1,
    #         'grading': 1,
    #         'address': 1
    #     })

    return render_template('results.template.html', all_stalls=all_stalls,)


# Display stall information and show form to create review
@app.route('/stall/<stall_id>/display')
def show_stall_info(stall_id):
    return render_template('display.template.html', stall_id=stall_id)

# Process form to create review
@app.route('/stall/<stall_id>/display', methods=["POST"])
def process_create_review():
    return redirect(url_for('show_stall_info'))


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
