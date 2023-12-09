from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from models import DJ, Voter

# Database configuration
#MONGODB_HOST = "localhost"
#MONGODB_PORT = 27017
#MONGODB_DB = "dj_ranking"
#MONGODB_COLLECTION_DJS = "djs"
#MONGODB_COLLECTION_VOTERS = "voters"
#MONGODB_COLLECTION_VOTES = "votes"

#Connect to MongoDB
uri = "mongodb+srv://alealferez123:BaJnBfrtkTluXZsD@djrank.lqulsiv.mongodb.net/?retryWrites=true&w=majority"
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://alealferez123:BaJnBfrtkTluXZsD@djrank.lqulsiv.mongodb.net/?retryWrites=true&w=majority"
mongo = PyMongo(app)
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

djs = mongo.db.DJ
voters = mongo.db.Voter


@app.route("/")
def home():
    djs = mongo.db.djs.find()
    return render_template("home.html")

@app.route("/dj/<dj_id>")
def dj_profile(dj_id):
    dj = mongo.db.djs.find_one({"_id": ObjectId(dj_id)})
    return render_template("dj_profile.html", dj=dj)

@app.route("/voter/<voter_id>")
def voter_profile(voter_id):
    voter = mongo.db.voters.find_one({"_id": ObjectId(voter_id)})
    return render_template("voter_profile.html", voter=voter)

@app.route("/vote/<dj_id>", methods=["GET", "POST"])
def vote(dj_id):
    dj = mongo.db.djs.find_one({"_id": ObjectId(dj_id)})
    if request.method == "GET":
        return render_template("vote.html", dj_id=dj_id)
    else:
        vote = int(request.form["vote"])
        voter_id = request.form["voter_id"]
        # Update DJ's ranking
        mongo.db.djs.update_one({"_id": ObjectId(dj_id)}, {"$inc": {"votes": vote}})
        # Add vote to voter's history
        mongo.db.voters.update_one({"_id": ObjectId(voter_id)}, {"$push": {"voted_djs": ObjectId(dj_id)}})
        return redirect(url_for("dj_profile", dj_id=dj_id))

@app.route("/register/dj", methods=["GET", "POST"])
def register_dj():
    if request.method == "POST":
        # Get form data
        name = request.form["name"]
        genre = request.form["genre"]
        bio = request.form["bio"]
        website = request.form.get("website")
        # Validate data
        errors = []
        if not name:
            errors.append("Name is required.")
        if not genre:
            errors.append("Genre is required.")
        if not bio:
            errors.append("Bio is required.")
        # Check if DJ already exists
        existing_dj = mongo.db.djs.find_one({"name": name})
        if existing_dj:
            errors.append("DJ with the same name already exists.")
        # If no errors, create new DJ document
        if not errors:
            dj = DJ(name=name, genre=genre, bio=bio, website=website, votes=0)
            mongo.db.djs.insert_one(dj.to_dict())
            return redirect(url_for("home"))
        # Render registration form with errors
        return render_template("register_dj.html", errors=errors)
    # Render registration form
    return render_template("register_dj.html")

@app.route("/register/voter")
def register_voter():
    if request.method == "POST":
        # Get form data
        name = request.form["name"]
        email = request.form["email"]
        favorite_genres = request.form.getlist("favorite_genres")
        # Validate data
        errors = []
        if not name:
            errors.append("Name is required.")
        if not email:
            errors.append("Email is required.")
        if not validate_email(email):
            errors.append("Invalid email address.")
        # Check if voter already exists
        existing_voter = mongo.db.voters.find_one({"email": email})
        if existing_voter:
            errors.append("Voter with the same email already exists.")
        # If no errors, create new voter document
        if not errors:
            voter = Voter(name=name, email=email, favorite_genres=favorite_genres, voted_djs=[])
            mongo.db.voters.insert_one(voter.to_dict())
            return redirect(url_for("home"))
        # Render registration form with errors
        return render_template("register_voter.html", errors=errors)
    # Render registration form
    return render_template("register_voter.html")
if __name__ == "__main__":
    app.run(debug=True, port=8080)