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
    all_hawker = db.hawkerCentres.find()
    return render_template('home.template.html', all_hawker=all_hawker)


# Process form for hawker centre search
@app.route('/', methods=["POST"])
def process_search_hawker():
    hawker_centre = request.form.get('hawker_centre_search')

    print(hawker_centre)

    

    # stalls_in_hawker = db.foodStalls.find({
    #     'hawker_centre': hawker_centre
    # }, {
    #     'stall_name':1,
    #     'hawker_centre':1,
    #     'specialty':1
    # })

    return redirect(url_for('show_stalls_in_hawker', hawker_centre=hawker_centre))


# Display stalls in selected hawker centre
@app.route('/stalls/<hawker_centre>')
def show_stalls_in_hawker(hawker_centre):
    stalls = db.foodStalls.find({
        'hawker_centre': hawker_centre
    }, {
        'stall_name':1,
        'hawker_centre':1,
        'specialty':1
    })
    return render_template('stalls_by_hawker.template.html', stalls=stalls)



# Create stall
# Show form to create stall
@app.route('/stall/create')
def show_create_stall():
    return render_template('create_stall.template.html')

# Process form to create stall
@app.route('/stall/create', methods=["POST"])
def process_create_stall():
    stall_name = request.form.get('stall_name')
    hawker_centre = request.form.get('hawker_centre')
    specialty = request.form.get('specialty')
    unit_no = request.form.get('unit_no')
    opening_hours = request.form.get('opening_hours')

    db.foodStalls.insert_one({
        "stall_name": stall_name,
        "hawker_centre": hawker_centre,
        "specialty": specialty,
        "unit_no": unit_no,
        "opening_hours": opening_hours
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
@app.route('/stall/<stall_id>/<stall_name>/<address>/display')
def show_stall_info(stall_id, stall_name, address):
    reviewed_stall_id = ObjectId(stall_id)

    stall_reviews = db.stallReviews.find({
        'reviewed_stall_id': reviewed_stall_id
    }, {
        'user_name':1,
        'comment':1
    })

    return render_template('display.template.html', stall_id=stall_id, stall_name=stall_name, address=address, stall_reviews=stall_reviews)

# Process form to create review
@app.route('/stall/<stall_id>/<stall_name>/<address>/display', methods=["POST"])
def process_create_review(stall_id, stall_name, address):
    user_name = request.form.get('user_name')
    comment = request.form.get('comment')
    reviewed_stall_name = stall_name
    reviewed_stall_id = ObjectId(stall_id)

    db.stallReviews.insert_one({
        "user_name": user_name.lower(),
        "comment": comment.lower(),
        "reviewed_stall_name": stall_name.lower(),
        "reviewed_stall_id": reviewed_stall_id
    })

    return redirect(url_for('show_stall_info', stall_id=stall_id, stall_name=stall_name, address=address))


# Update stall
@app.route('/stall/<stall_id>/update')
def show_update_stall(stall_id):
    stall = db.foodStalls.find_one({
        '_id': ObjectId(stall_id)
    })
    return render_template('show_update_stall.template.html',
                           stall=stall)

# Process to update stall
@app.route('/stall/<stall_id>/update', methods=["POST"])
def process_update_stall(stall_id):
    db.foodStalls.update_one({
        "_id": ObjectId(stall_id)
    }, {
        '$set': request.form
    })
    return redirect(url_for('show_all_stalls'))



# Delete stall
@app.route('/stall/<stall_id>/delete')
def delete_stall(stall_id):
    stall = db.foodStalls.find_one({
        '_id': ObjectId(stall_id)
    })

    return render_template('confirm_delete_stall.template.html', stall=stall)

# Process to delete stall
@app.route('/stall/<stall_id>/delete', methods=['POST'])
def process_delete_stall(stall_id):

    db.foodStalls.remove({
        '_id': ObjectId(stall_id)
    })

    return redirect(url_for('show_all_stalls'))


# Update review
@app.route('/review/<review_id>/update')
def show_update_review(review_id):
    review = db.stallReviews.find_one({
        '_id': ObjectId(review_id)
    })
    return render_template('show_update_review.template.html',
                           review=review)

# Process to update review
@app.route('/review/<review_id>/update', methods=["POST"])
def process_update_review(review_id):
    db.stallReviews.update_one({
        "_id": ObjectId(review_id)
    }, {
        '$set': request.form
    })
    return redirect(url_for('show_all_stalls'))




# Delete review
@app.route('/review/<review_id>/delete')
def delete_review(review_id):
    review = db.stallReviews.find_one({
        '_id': ObjectId(review_id)
    })

    return render_template('confirm_delete_review.template.html', review=review)

# Process to delete review
@app.route('/review/<review_id>/delete', methods=['POST'])
def process_delete_review(review_id):

    db.stallReviews.remove({
        '_id': ObjectId(review_id)
    })

    return redirect(url_for('show_all_stalls'))






if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
