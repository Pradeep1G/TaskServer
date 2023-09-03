
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_cors import CORS
from flask_mail import Mail, Message
from pymongo.errors import InvalidOperation, DuplicateKeyError
import random
import jwt
import datetime

from dotenv import load_dotenv
import os

app=Flask(__name__)
CORS(app)



app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Replace with your email server
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'pradeepgeddada31@gmail.com'  # Replace with your email address
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')  # Replace with your email password

mail = Mail(app)



client = MongoClient(os.environ.get('MONGO_URI'))

# mongodb+srv://PradeeP1G:Pradeep%402003@cluster0.50omidk.mongodb.net

db = client.TaskMPeople

CORS(app)



@app.route('/checkUser', methods=['POST'])
def checkUser():
    data = request.json
    email = data['mail']
    password = data['password']
    filter = {'email':email}
    collection = db.Users  # Replace <collection_name> with the name of your collection
    result = collection.find_one(filter)
    print(result)
    if result is None:
        return jsonify({"act_available":False})
    else:
        if result['password']==password:
            return jsonify({"act_available":True, "is_password_correct":True})
        else:
            return jsonify({'act_available':True, 'is_password_correct':False})

@app.route('/addUser', methods=['PUT'])
def addUser():
    data = request.json
    email=data['email']
    password=data['password']
    name=data['name']
    collection = db.Users
    result = collection.insert_one(data)
    if result:
        return jsonify({"is_registered":True})
    else:
        return jsonify({"is_registered":False})
    
@app.route("/verifyMail/<string:mailid>", methods=["POST"])
def verifyMail(mailid):
    data = request.json
    
    collection = db.Users
    result = collection.find_one(data)

    if result is None:
        
        otp = random.randint(100000,999999)

        try:
            msg = Message('OTP to Register in Tasker',
                          sender="prfadeepgeddada31@gmail.com",
                          recipients=[mailid])
            msg.body = f'Dear customer, \nYour OTP is {otp}, for registering in Tasker website.Please enter thus OTP on the request screen to complete the Tasker authentication process.\nRegards,\nTasker Services.'
            mail.send(msg)
            return jsonify({"Act_already_Registered":False, "isOTPsent":True, "OTP":otp})
        except Exception as e:
            print(e)
            return jsonify({"Act_already_Registered":False, "isOTPsent":False})
    
    else:
        return jsonify({"Act_already_Registered":True})










if __name__ == '__main__':
    app.debug = True
    app.run()
