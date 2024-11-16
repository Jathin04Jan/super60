from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from bson.errors import InvalidId

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/Super60Database"
mongo = PyMongo(app)

# Home page
@app.route("/")
def home():
    students = list(mongo.db.studentDetails.find())
    for student in students:
        print(f"Student ID: {student['_id']}")  # Debug: Print each student's ID
        student["_id"] = str(student["_id"])    #converts objectID to string
    return render_template("index.html", students= students)

# Searching part, (Search bar in home page)
@app.route("/search")
def search():
    query = request.args.get('name', '')
    students = mongo.db.studentDetails.find({"name": {"$regex": query, "$options": "i"}})
    return render_template("index.html", students = students)

# Individual student profiles
@app.route("/profile/<student_id>")
def profile(student_id):
    try:
        #Finding the students by their unique object id
        print(f"Received student_id: {student_id}")  # Debug
        student = mongo.db.studentDetails.find_one({"_id": ObjectId(student_id)})
        print(f"Found student: {student}")  # Debug
        if not student:
            return "Student Not found", 404
        return render_template("profile.html", student= student)
    except InvalidId:
        return "Invalid student ID!", 400
    except Exception as e:
        return f"An error occured: {e}", 500
    
# For individual student remarks
@app.route("/profile/<student_id>/remarks", methods= ["post"])
def update_remarks(student_id):
    try:
        #Getting the remarks from the form
        remarks = request.form.get("remarks")

        # Update the student's document in MongoDB
        mongo.db.studentDetails.update_one(
            {"_id": ObjectId(student_id)},
            {"$set": {"remarks": remarks}}
        )
        # Redirect back to the profile page
        return redirect(url_for("profile", student_id=student_id))
    except Exception as e:
        return f"An error occurred: {e}", 500

#Add student button
@app.route("/add-student", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        #Get student detals from the form
        name = request.form.get("name")
        age = request.form.get("age")
        course = request.form.get("course")
        remarks = request.form.get("remarks")

        # Insert the new student into the database
        mongo.db.studentDetails.insert_one({
            "name": name,
            "age": int(age),
            "course": course,
            "remarks": remarks or "" #default to empty string if no remarks
        })

        # Redirect back to the home page
        return redirect(url_for("home"))

    # Render the form to add a new student
    return render_template("add_student.html")
    
#Edit student button
@app.route("/profile/<student_id>/edit", methods=["GET", "POST"])
def edit_student(student_id):
    if request.method == "POST":
        # Get updated student details from the form
        name = request.form.get("name")
        age = request.form.get("age")
        course = request.form.get("course")
        remarks = request.form.get("remarks")

        # Update the student record in MongoDB
        mongo.db.studentDetails.update_one(
            {"_id": ObjectId(student_id)},
            {
                "$set": {
                    "name": name,
                    "age": int(age),
                    "course": course,
                    "remarks": remarks or ""
                }
            }
        )

        # Redirect back to the profile page
        return redirect(url_for("profile", student_id=student_id))

    # Fetch the student's current details to pre-fill the form
    student = mongo.db.studentDetails.find_one({"_id": ObjectId(student_id)})
    if not student:
        return "Student not found!", 404

    return render_template("edit_student.html", student=student)


if __name__ == "__main__":
    app.run(debug= True, port= 5069)