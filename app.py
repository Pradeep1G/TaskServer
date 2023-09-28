
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_cors import CORS
from flask_mail import Mail, Message
from pymongo.errors import InvalidOperation, DuplicateKeyError
import random
import jwt
import datetime
import json

from dotenv import load_dotenv
import os

app=Flask(__name__)
CORS(app)
# CORS(app, resources={r"/": {"origins": "https://main--tasks-manager-site.netlify.app"}})





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
            return jsonify({"act_available":True, "is_password_correct":True, "name":result['name']})
        else:
            return jsonify({'act_available':True, 'is_password_correct':False})

@app.route('/addUser', methods=['PUT'])
def addUser():
    data = request.json
    email=data['email']
    password=data['password']
    name=data['name']

    collection_data = {
        "WorkSpace0": {
            "bgColor":"#fff",
            "ToDo" : {
                "AllWorks":[]
            },
            "Doing" : {
                "AllWorks":[]
            },
            "Done" : {
                "AllWorks":[]
            }
        }
    }

    collection = db.Users
    result = collection.insert_one(data)
    AllUsersCollectionsDB = client.AllUsersCollections
    newCollecton = AllUsersCollectionsDB[data['dbname']]
    inserted_data = newCollecton.insert_one(collection_data)




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
    
@app.route("/forgetPassword/<string:mailid>", methods=["POST"])
def forgetPassword(mailid):
    data = request.json
    db=client.TaskMPeople
    collection = db.Users
    filter = {'email':data['mail']}

    result = collection.find_one(filter)

    print(result)
    if result:

        password = result["password"]
        otp = random.randint(100000,999999)

        try:
            msg = Message('Confidential Message from Tasker',
                          sender="prfadeepgeddada31@gmail.com",
                          recipients=[mailid])
            msg.body = f'Dear customer, \n We have a request from this mail id to send your account password. Do not forget your password next time.YourPasswordIs{password}Please delete this message after viewing.  \nRegards,\nTasker Services.'
            mail.send(msg)
            return jsonify({"message":"Your password is sent to your mail."})
        except Exception as e:
            return jsonify({"message":"Something went wrong, please Try after sometime."})

    else:
        return jsonify({"message":"Mail Not Found"})


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

app.json_encoder = CustomJSONEncoder


@app.route("/getUserData", methods=["POST"])
def getUserData():
    data = request.json
    # print(data)
    
    db=client.AllUsersCollections

    
    collection = db[data["collectionName"]]
    data = list(collection.find({}))
    # print(data)
    return jsonify({"data":data})


@app.route("/addWorkspace", methods=["POST"])
def addWorkspace():
    data = request.json

    db=client.AllUsersCollections
    collection = db[data["collectionName"]]

    data = list(collection.find({}))

    

    newWorkspace = "WorkSpace"+str(len(data[0])-1)
    print(newWorkspace)

    newData =   {
            "bgColor":"#fff",
            "ToDo" : {
                "AllWorks":[]
            },
            "Doing" : {
                "AllWorks":[]
            },
            "Done" : {
                "AllWorks":[]
            }
        }
    



    filter = {
        f'WorkSpace0':{
            "$exists":True
        }
    }
                
    update={
        "$set" : {
            f"{newWorkspace}":newData
        }
        }
    
    result = collection.update_one(filter, update)
    print(result.modified_count)



    if result.acknowledged:
        return jsonify({"message": "Successfully Added WorkSpace"})
    else:
        return jsonify({"error": "Failed to Add WorkSpace"})




@app.route("/updateEventData", methods=["POST"])
def update_event_data():
    try:
        # Get data from the request
        data = request.json
        collection_name = data.get("collectionName")
        workspace = data.get("WorkSpace")
        work_type = data.get("type")
        work_name = data.get("workName")
        updated_work_name = data.get("updatedWorkName")
        updated_data = data.get("updatedData")

        db = client.AllUsersCollections

        # Specify the filter to match the document you want to update
        filter = { f"{workspace}.{work_type}.{work_name}": {
                        "$exists": True
                    }
            }
        

        # print(list(db[collection_name].find({f'{workspace}.{work_type}':{"$exists":True}})))
        

        # print(data)
        # Update the document using the $set operator


        if work_name=="":
            # print(data)
            
            if updated_work_name:

                print(data)

                
                filter = { f"{workspace}.{work_type}": {
                        "$exists": True
                    }
                }
                
                update={
                    "$set" : {
                        f"{workspace}.{work_type}.{updated_work_name}":updated_data
                    },
                        "$push": {f"{workspace}.{work_type}.AllWorks": updated_work_name}
                }
                
                result = db[collection_name].update_one(filter, update)
                print(result.modified_count)



        else:
               

            if work_name != updated_work_name:

                update = {
                    "$set": {
                        f"{workspace}.{work_type}.{updated_work_name}": updated_data
                    },
                        "$push": {f"{workspace}.{work_type}.AllWorks": updated_work_name}
                }
            else:
                update = {
                    "$set": {
                        f"{workspace}.{work_type}.{work_name}": updated_data
                    }
                }

            # Update the AllEvents array with the new event name if it has changed
            # if work_name != updated_work_name:
            #     update["$push"] = {f"{workspace}.{work_type}.AllWorks": updated_work_name}
            #     update["$"]

            # Update the document in the specified collection
            result = db[collection_name].update_one(filter, update)

        if result.modified_count == 1:
            # print(data)
            # Check if the event name needs to be updated
            if work_name != updated_work_name and work_name!="":
                print(data)
                # If the event name has changed, remove the old event
                update1 = {
                    "$unset": {
                        f"{workspace}.{work_type}.{work_name}": ""
                    }
                }
                db[collection_name].update_one(filter, update1)

                filter = { f"{workspace}.{work_type}.AllWorks": {
                        "$exists": True
                }
                }

            

                pull_update = {
                    "$pull": {f"{workspace}.{work_type}.AllWorks": work_name}
                }
                db[collection_name].update_one(filter, pull_update)

                
            return jsonify({"message": "Document updated successfully"})
        else:
            return jsonify({"message": "Document not found or not updated"})

    except Exception as e:
        return jsonify({"error": str(e)})



@app.route("/shiftEvent", methods=["POST"])
def sfiftEvent():
    data = request.json

    print(data)

    db = client.AllUsersCollections
    collection = db[data["collectionName"]]
    work_space = data["WorkSpace"]
    type_to_add = data["typeToAdd"]
    work_to_add = data["workToAdd"]
    data_to_add = data["dataToAdd"]
    type_to_delete = data["typeToDelete"]
    work_to_delete = data["workToDelete"]

    print(work_space,type_to_add,work_to_add,data_to_add)

    # data_to_insert = {work_to_add:data_to_add}


    addFilter = { f"{work_space}.{type_to_add}" : {
                        "$exists": True
                }
    }

    try:
        # Get the work item to insert and the workspace name from the request
        
        if not work_to_add or not work_space:
            return jsonify({"message": "Invalid request data."}), 400

        # Find the document you want to update (replace the query with your criteria)
        query = {"_id": "64f607413b49a69c4e5bd1ac"}  # Replace with your query criteria
        documents = collection.find({})
        # print(documents)

        # Check if any documents were found
        if documents:
            # print("Success")
            # Loop through the documents
            for doc in documents:
                # print(doc["WorkSpace0"]['Doing'])

                # Check if the work item already exists in the "Doing" section
                if work_to_add in doc[work_space][type_to_add]["AllWorks"]:
                    print("success")
                    return jsonify({"message": f"Work '{work_to_add}' already exists in the Doing section."}), 400

                print("Success")
                # Add the work item to "Doing"
                doc[work_space][type_to_add]["AllWorks"].append(work_to_add)
                doc[work_space][type_to_add][work_to_add] = data_to_add

                
                 # Remove the work item from the old type
                if work_to_delete in doc[work_space][type_to_delete]["AllWorks"]:
                    doc[work_space][type_to_delete]["AllWorks"].remove(work_to_delete)
                    del doc[work_space][type_to_delete][work_to_delete]
                    

                # Save the updated document back to the collection
                collection.replace_one({"_id": doc["_id"]}, doc)



            return jsonify({"message": f"Work '{work_to_add}' inserted into Doing successfully."}), 200
        else:
            return jsonify({"message": "Document not found."}), 404
    except Exception as e:
        # print(jsonify(e))
        return jsonify({"message": str(e)}), 500
    
@app.route('/deleteEvent', methods=['OPTIONS'])
def handle_preflight():
    return '', 204  # No content in the response for preflight requests


@app.route("/deleteEvent", methods=["POST"])
def deleteEvent():
    data = request.json
    print(data)

    # collection_name = data.get("collectionName")
    workspace = data.get("WorkSpace")
    event_type = data.get("eventType")
    event_name = data.get("eventName")
    db = client.AllUsersCollections
    collection = db[data["collectionName"]]

    filter = {
        f'{workspace}.{event_type}.{event_name}':{"$exists":True}
    }
    update = {
        "$unset":{
            f'{workspace}.{event_type}.{event_name}':""
        }
    }
    result = collection.update_one(filter, update)

    filter1 = { f"{workspace}.{event_type}.AllWorks": {
                        "$exists": True
                }
                }

            

    pull_update = {
        "$pull": {f"{workspace}.{event_type}.AllWorks": event_name}
    }
    result1 = collection.update_one(filter1, pull_update)



    print(result1.modified_count)
    


    return jsonify({"messege":"connected"})



@app.route('/addAWSWeatherUser', methods=['PUT'])
def addUser():
    data = request.json

    db = client.awslambda
    
    collection = db.weatherusers
    result = collection.insert_one(data)
    




    if result:
        print("Success")
        return jsonify({"is_success":True})
    else:
        return jsonify({"is_success":False})
    
            




if __name__ == '__main__':
    app.debug = True
    app.run()
