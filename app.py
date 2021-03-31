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

@app.route('/stall/results')
def show_search_results():
    find_stall_name = str(request.args.get('find_stall_name'))

    criteria = {}

    if find_stall_name:

        criteria['stall_name'] = {'$regex': find_stall_name, '$options': 'i'}

        search_stall = db.foodStalls.find(criteria, {
            'stall_name': 1,
            'area': 1,
            'grading': 1,
            'address': 1
        })
    return render_template('results.template.html', search_stall=search_stall)






# # Delete stall
# @app.route('/stall/<stall_id>/delete')
# def delete_stall(stall_id):
#     stall = db.foodStalls.find_one({
#         '_id': ObjectId(stall_id)
#     })

#     return render_template('confirm_delete_stall.template.html',
#                            stall_to_delete=stall)


# @app.route('/stall/<stall_id>/delete', methods=["POST"])
# def process_delete_stall(stall_id):
#     db.foodStalls.remove({
#         "_id": ObjectId(stall_id)
#     })
#     return redirect(url_for('show_search_results'))


# Display page
@app.route('/stall/display')
def show_stall_info():
    return render_template('display.template.html')


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
