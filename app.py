from flask import Flask, render_template, request, redirect, url_for, flash
import os
import pymongo
from dotenv import load_dotenv

from bson.objectid import ObjectId

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

MONGO_URI = os.environ.get('MONGO_URI')
DB_NAME = 'thr_db'

client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]


# Home page
@app.route('/')
def home():
    all_hawker = db.hawkerCentres.find()
    return render_template('home.template.html',
                           all_hawker=all_hawker,
                           errors={})


# Process form for hawker centre search
@app.route('/', methods=["POST"])
def process_search_hawker():
    hawker_centre = request.form.get('hawker_centre_search')

    errors = {}
    if hawker_centre == "":
        errors['hawker_centre'] = "Please select a hawker centre"

    if len(errors) == 0:
        return redirect(url_for('show_stalls_in_hawker',
                                hawker_centre=hawker_centre))
    else:
        all_hawker = db.hawkerCentres.find()
        return render_template('home.template.html',
                               all_hawker=all_hawker,
                               errors=errors)


# Return results for hawker centre search
@app.route('/stalls/<hawker_centre>')
def show_stalls_in_hawker(hawker_centre):
    stalls = db.foodStalls.find({
        'hawker_centre': hawker_centre
    }, {
        'stall_name': 1,
        'hawker_centre': 1,
        'specialty': 1,
        'image_url': 1
    })
    return render_template('stalls_by_hawker.template.html',
                           stalls=stalls)


# Search by preference
@app.route('/stall/results')
def filter_stall():
    find_stall = str(request.args.get('find_stall'))
    find_specialty = str(request.args.get('find_specialty'))

    criteria_stall = {}

    if find_stall:
        criteria_stall['stall_name'] = {'$regex': find_stall, '$options': 'i'}

    if find_specialty:
        criteria_stall['specialty'] = {
            '$regex': find_specialty, '$options': 'i'}

    display_stall = db.foodStalls.find(criteria_stall, {
        'stall_name': 1,
        'hawker_centre': 1,
        'specialty': 1,
        'image_url': 1
    })
    return render_template('results.template.html',
                           display_stall=display_stall)


# Create stall
# Show form to create stall
@app.route('/stall/create')
def show_create_stall():
    all_hawker = db.hawkerCentres.find()
    return render_template('create_stall.template.html',
                           all_hawker=all_hawker,
                           errors={},
                           old_values={})


# Process form to create stall
@app.route('/stall/create', methods=["POST"])
def process_create_stall():
    stall_name = request.form.get('stall_name')
    hawker_centre = request.form.get('hawker_centre')
    specialty = request.form.get('specialty')
    unit_no = request.form.get('unit_no')
    opening_hours = request.form.get('opening_hours')

    errors = {}
    if stall_name == "":
        errors['stall_name'] = "Stall name cannot be blank"

    if hawker_centre == "":
        errors['hawker_centre'] = "Please select a hawker centre"

    if specialty == "":
        errors['specialty'] = "Specialty dish cannot be blank"

    if unit_no == "":
        errors['unit_no'] = "Unit number cannot be blank"

    if opening_hours == "":
        errors['opening_hours'] = "Opening hours cannot be blank"

    if len(errors) == 0:
        db.foodStalls.insert_one({
            "stall_name": stall_name,
            "hawker_centre": hawker_centre,
            "specialty": specialty,
            "unit_no": unit_no,
            "opening_hours": opening_hours
        })
        flash("New stall has been created!")
        return redirect(url_for('show_create_stall'))
    else:
        all_hawker = db.hawkerCentres.find()
        return render_template('create_stall.template.html',
                               all_hawker=all_hawker,
                               errors=errors,
                               old_values=request.form)


# Display stall information and show form to create review
@app.route('/stall/<stall_id>/<stall_name>/<hawker_centre>/display')
def show_stall_info(stall_id, stall_name, hawker_centre):
    reviewed_stall_id = ObjectId(stall_id)

    stall_to_display = db.foodStalls.find({
        '_id': reviewed_stall_id
    }, {
        'stall_name': 1,
        'hawker_centre': 1,
        'specialty': 1,
        'unit_no': 1,
        'opening_hours': 1
    })

    hawker_to_display = db.hawkerCentres.find({
        'name': hawker_centre
    }, {
        'address': 1
    })

    stall_reviews = db.stallReviews.find({
        'reviewed_stall_id': reviewed_stall_id
    }, {
        'user_name': 1,
        'comment': 1
    })
    return render_template('display.template.html',
                           stall_id=stall_id,
                           stall_name=stall_name,
                           stall_reviews=stall_reviews,
                           stall_to_display=stall_to_display,
                           hawker_to_display=hawker_to_display,
                           errors={},
                           old_values={})


# Process form to create review
@app.route('/stall/<stall_id>/<stall_name>/<hawker_centre>/display',
           methods=["POST"])
def process_create_review(stall_id, stall_name, hawker_centre):
    user_name = request.form.get('user_name')
    comment = request.form.get('comment')
    reviewed_stall_id = ObjectId(stall_id)

    errors = {}
    if user_name == "":
        errors['user_name'] = "Enter a username"

    if comment == "":
        errors['comment'] = "Enter your comments"

    if len(errors) == 0:
        db.stallReviews.insert_one({
            "user_name": user_name,
            "comment": comment,
            "reviewed_stall_name": stall_name,
            "reviewed_stall_id": reviewed_stall_id
        })
        flash("New review created!")
        return redirect(url_for('show_stall_info',
                                stall_id=stall_id,
                                stall_name=stall_name,
                                hawker_centre=hawker_centre))
    else:
        reviewed_stall_id = ObjectId(stall_id)

        stall_to_display = db.foodStalls.find({
            '_id': reviewed_stall_id
        }, {
            'stall_name': 1,
            'hawker_centre': 1,
            'specialty': 1,
            'unit_no': 1,
            'opening_hours': 1
        })

        hawker_to_display = db.hawkerCentres.find({
            'name': hawker_centre
        }, {
            'address': 1
        })

        stall_reviews = db.stallReviews.find({
            'reviewed_stall_id': reviewed_stall_id
        }, {
            'user_name': 1,
            'comment': 1
        })

        return render_template('display.template.html',
                               stall_id=stall_id,
                               stall_name=stall_name,
                               stall_reviews=stall_reviews,
                               stall_to_display=stall_to_display,
                               hawker_to_display=hawker_to_display,
                               errors=errors,
                               old_values=request.form)


# Update stall
@app.route('/stall/<stall_id>/update')
def show_update_stall(stall_id):
    all_hawker = db.hawkerCentres.find()

    stall = db.foodStalls.find_one({
        '_id': ObjectId(stall_id)
    })
    return render_template('show_update_stall.template.html',
                           all_hawker=all_hawker,
                           stall=stall,
                           errors={},
                           old_values={})


# Process to update stall
@app.route('/stall/<stall_id>/update', methods=["POST"])
def process_update_stall(stall_id):
    stall_name = request.form.get('stall_name')
    hawker_centre = request.form.get('hawker_centre')
    specialty = request.form.get('specialty')
    unit_no = request.form.get('unit_no')
    opening_hours = request.form.get('opening_hours')

    errors = {}
    if stall_name == "":
        errors['stall_name'] = "Stall name cannot be blank"

    if hawker_centre == "":
        errors['hawker_centre'] = "Please select a hawker centre"

    if specialty == "":
        errors['specialty'] = "Specialty dish cannot be blank"

    if unit_no == "":
        errors['unit_no'] = "Unit number cannot be blank"

    if opening_hours == "":
        errors['opening_hours'] = "Opening hours cannot be blank"

    if len(errors) == 0:
        db.foodStalls.update_one({
            "_id": ObjectId(stall_id)
        }, {
            '$set': request.form
        })
        flash("Stall info has been updated!")
        return redirect(url_for('show_stall_info',
                                stall_id=stall_id,
                                stall_name=stall_name,
                                hawker_centre=hawker_centre))
    else:
        all_hawker = db.hawkerCentres.find()
        old_values = {**request.form}
        stall = db.foodStalls.find_one({
            '_id': ObjectId(stall_id)
        })
        return render_template('show_update_stall.template.html',
                               all_hawker=all_hawker,
                               stall=stall,
                               errors=errors,
                               old_values=old_values)


# Delete stall
@app.route('/stall/<stall_id>/delete')
def delete_stall(stall_id):
    stall = db.foodStalls.find_one({
        '_id': ObjectId(stall_id)
    })
    return render_template('confirm_delete_stall.template.html',
                           stall=stall)


# Process to delete stall
@app.route('/stall/<stall_id>/delete', methods=['POST'])
def process_delete_stall(stall_id):
    db.foodStalls.remove({
        '_id': ObjectId(stall_id)
    })
    flash("Stall has been deleted!")
    return redirect(url_for('home'))


# Update review
@app.route('/review/<review_id>/update')
def show_update_review(review_id):
    review = db.stallReviews.find_one({
        '_id': ObjectId(review_id)
    })
    return render_template('show_update_review.template.html',
                           review=review,
                           errors={},
                           old_values={})


# Process to update review
@app.route('/review/<review_id>/update', methods=["POST"])
def process_update_review(review_id):
    user_name = request.form.get('user_name')
    comment = request.form.get('comment')

    errors = {}
    if user_name == "":
        errors['user_name'] = "Enter a username"

    if comment == "":
        errors['comment'] = "Enter your comments"

    if len(errors) == 0:
        review = db.stallReviews.find_one({
            '_id': ObjectId(review_id)
        })
        stall_id = review['reviewed_stall_id']

        stall = db.foodStalls.find_one({
            '_id': ObjectId(stall_id)
        })
        stall_name = stall['stall_name']
        hawker_centre = stall['hawker_centre']

        db.stallReviews.update_one({
            "_id": ObjectId(review_id)
        }, {
            '$set': request.form
        })
        flash("Review has been updated!")
        return redirect(url_for('show_stall_info',
                                stall_id=stall_id,
                                stall_name=stall_name,
                                hawker_centre=hawker_centre))
    else:
        old_values = {**request.form}
        review = db.stallReviews.find_one({
            '_id': ObjectId(review_id)
        })
        return render_template('show_update_review.template.html',
                               review=review,
                               errors=errors,
                               old_values=old_values)


# Delete review
@app.route('/review/<review_id>/delete')
def delete_review(review_id):
    review = db.stallReviews.find_one({
        '_id': ObjectId(review_id)
    })
    stall_id = review['reviewed_stall_id']

    stall = db.foodStalls.find_one({
        '_id': ObjectId(stall_id)
    })
    return render_template('confirm_delete_review.template.html',
                           review=review,
                           stall=stall)


# Process to delete review
@app.route('/review/<review_id>/delete', methods=['POST'])
def process_delete_review(review_id):

    review = db.stallReviews.find_one({
        '_id': ObjectId(review_id)
    })
    stall_id = review['reviewed_stall_id']

    stall = db.foodStalls.find_one({
        '_id': ObjectId(stall_id)
    })
    stall_name = stall['stall_name']
    hawker_centre = stall['hawker_centre']

    db.stallReviews.remove({
        '_id': ObjectId(review_id)
    })
    flash("Review has been deleted!")
    return redirect(url_for('show_stall_info',
                            stall_id=stall_id,
                            stall_name=stall_name,
                            hawker_centre=hawker_centre))


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
