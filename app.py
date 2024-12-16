from flask import Flask, Blueprint, render_template, request, jsonify
from config import app,db
from models import Task,Reminder
from datetime import datetime, timedelta

#get all tasks 
@app.route("/tasks", methods=["GET"])
def get_tasks():
        tasks = Task.query.all()
        json_tasks = [{"id": task.id,
                       "name": task.name, 
                       "priority": task.priority,
                       "category": task.category,
                       "deadline": task.deadline

                       } for task in tasks]
        return jsonify({"tasks": json_tasks})

#get all tasks by priority
@app.route("/tasks/priority/<string:priority>", methods=["GET"])
def get_tasks_by_priority(priority):    
    valid_priorities = ["High", "Medium", "Low"]
    if priority not in valid_priorities:
        return jsonify({"error": "Invalid priority. Please use High, Medium, or Low."}), 400

    tasks = Task.query.filter_by(priority=priority).all()

    json_tasks = [{"id": task.id,
                   "name": task.name,
                   "priority": task.priority,
                   "category": task.category,
                   "deadline": task.deadline
                   } for task in tasks]

    return jsonify({"tasks": json_tasks})

#get tasks by category
@app.route("/tasks/category/<string:category>", methods=["GET"])
def get_tasks_by_category(category):
    # Validate the category input
    valid_categories = ["Personal", "Work"]
    if category not in valid_categories:
        return jsonify({"error": "Invalid category. Please use Personal or Work."}), 400

    # Query the tasks with the given category
    tasks = Task.query.filter_by(category=category).all()

    # Serialize the task data
    json_tasks = [{"id": task.id,
                   "name": task.name,
                   "priority": task.priority,
                   "category": task.category,
                   "deadline": task.deadline
                   } for task in tasks]

    return jsonify({"tasks": json_tasks})

#get tasks by name
@app.route("/tasks/name/<string:name>", methods=["GET"])
def get_tasks_by_name(name):
    #split the input name into words
    input_words = name.lower().split()
    
    tasks = Task.query.all()
    
    #tasks with maximum word match
    matched_tasks = []
    max_word_match = 0
    
    for task in tasks:
        #task name into words
        task_words = task.name.lower().split()
        
        # Count matching words
        matching_words = sum(1 for word in input_words if word in task_words)
        
        #matched tasks based on word match
        if matching_words > max_word_match:
            matched_tasks = [task]
            max_word_match = matching_words
        elif matching_words == max_word_match:
            matched_tasks.append(task)
    
    # Convert matched tasks to JSON
    json_tasks = [
        {
            "id": task.id, 
            "name": task.name, 
            "priority": task.priority, 
            "category": task.category, 
            "deadline": task.deadline.isoformat()
        } for task in matched_tasks
    ]
    
    return jsonify({"tasks": json_tasks, "max_word_match": max_word_match})

#get all reminders
@app.route("/reminders", methods=["GET"])
def get_reminders():
        reminders = Reminder.query.all()
        json_reminders = [{"id": reminder.id, 
                           "name": reminder.name, 
                           "category": reminder.category,
                           "priority": reminder.priority,
                           "time": reminder.time
                           
                           } for reminder in reminders]
        return jsonify({"reminders": json_reminders})
        
#get all reminders by priority       
@app.route("/reminders/priority/<string:priority>", methods=["GET"])
def get_reminders_by_priority(priority):
        
        valid_priorities = ["High", "Medium", "Low"]
        if priority not in valid_priorities:
             return jsonify({"error": "Invalid priority. Please use High, Medium, or Low."}), 400

        reminders = Reminder.query.filter_by(priority=priority).all()

        json_reminders = [{"id": reminder.id, 
                           "name": reminder.name, 
                           "category": reminder.category,
                           "priority": reminder.priority,
                           "time": reminder.time
                           
                           } for reminder in reminders]
        return jsonify({"reminders": json_reminders})
        
#get reminders by category
@app.route("/reminders/category/<string:category>", methods=["GET"])
def get_reminders_by_category(category):
    valid_categories = ["Personal", "Work"]
    if category not in valid_categories:
        return jsonify({"error": "Invalid category. Please use Personal or Work."}), 400

    reminders = Reminder.query.filter_by(category=category).all()

    json_reminders = [{"id": reminder.id,
                   "name": reminder.name,
                   "priority": reminder.priority,
                   "category": reminder.category,
                   "time": reminder.time
                   } for reminder in reminders]

    return jsonify({"reminders": json_reminders})

#get reminder by name
@app.route("/reminders/name/<string:name>", methods=["GET"])
def get_reminders_by_name(name):
    input_words = name.lower().split()
    
    reminders = Reminder.query.all()
    
    #reminders with maximum word match
    matched_reminders = []
    max_word_match = 0
    
    for reminder in reminders:
        # Split task name into words
        reminder_words = reminder.name.lower().split()
        
        #matching words
        matching_words = sum(1 for word in input_words if word in reminder_words)
        
        #matched reminders based on word match
        if matching_words > max_word_match:
            matched_reminders = [reminder]
            max_word_match = matching_words
        elif matching_words == max_word_match:
            matched_reminders.append(reminder)
    
    #matched reminders to JSON
    json_reminders = [
        {
            "id": reminder.id, 
            "name": reminder.name, 
            "priority": reminder.priority, 
            "category": reminder.category, 
            "time": reminder.time 
        } for reminder in matched_reminders
    ]
    
    return jsonify({"reminders": json_reminders})

#create new task
@app.route("/create_task", methods=["POST"])   
@app.route("/tasks/create", methods=["POST"]) 
def create_task():
        name = request.json.get("name")  
        priority = request.json.get("priority")  
        category = request.json.get("category")  
        deadline = request.json.get("deadline")

        if not name:
            return (
            jsonify({"message": "You must enter a descriptive task!"}),
            400,
            )
        
        try:
            if deadline:  
                deadline = datetime.strptime(deadline, "%Y-%m-%d %H:%M:%S")
        except ValueError:
                return (
            jsonify({"message": "Invalid time format. Use YYYY-MM-DD HH:MM:SS."}),
            400,
        )

        
        new_task = Task(name=name, priority=priority, deadline=deadline, category=category)
        try:
            db.session.add(new_task)
            db.session.commit()
        except Exception as e:
            return (
            jsonify({"message": str(e)}),
            400
            )
        return  jsonify({"message": "Task Created!"}), 201


#create new reminder
@app.route("/create_reminder", methods=["POST"])   
@app.route("/reminders/create", methods=["POST"]) 
def create_reminder():
        name = request.json.get("name")  
        priority = request.json.get("priority")  
        time = request.json.get("time")
        category = request.json.get("category")
        
        if not name:
            return (
            jsonify({"message": "You must enter a descriptive reminder!"}),
            400,
            )
        
        try:
            if time:  
                time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
        except ValueError:
                return (
            jsonify({"message": "Invalid time format. Use YYYY-MM-DD HH:MM:SS."}),
            400,
        )

        new_reminder = Reminder(name=name, priority=priority, time=time, category=category)
        try:
            db.session.add(new_reminder)
            db.session.commit()
        except Exception as e:
            return (
            jsonify({"message": str(e)}),
            400
            )
        return  jsonify({"message": "Reminder Created!"}), 201

#update task
@app.route("/update_task/<int:task_id>", methods=["PATCH"])
@app.route("/tasks/update/<int:task_id>", methods=["PATCH"])
def update_task(task_id):
        task= Task.query.get(task_id)
        if not task:
            return  jsonify({"message": "Task Not Found!"}), 404
        
        data = request.json
        task.name = data.get("name", task.name)
        task.priority = data.get("priority", task.priority)
        task.deadline = data.get("deadline", task.deadline)
        task.category = data.get("category", task.category)

        if task.deadline:  # Only update if deadline is provided
            try:
                task.deadline = datetime.strptime(task.deadline, "%Y-%m-%d %H:%M:%S")
            except ValueError:
             return jsonify({"message": "Invalid deadline format. Use YYYY-MM-DD HH:MM:SS."}), 400


        db.session.commit()
        return  jsonify({"message": "Task Updated!"}), 200

#update reminder
@app.route("/reminders/update/<int:reminder_id>", methods=["PATCH"])
@app.route("/update_reminder/<int:reminder_id>", methods=["PATCH"])
def update_reminder(reminder_id):
        reminder= Reminder.query.get(reminder_id)
    
        if not reminder:
            return  jsonify({"message": "Reminder Not Found!"}), 404
        
        data = request.json
        reminder.name = data.get("name", reminder.name)
        reminder.priority = data.get("priority", reminder.priority)
        reminder.time = data.get("time", reminder.time)
        reminder.category = data.get("category", reminder.category)

        if reminder.time:  # Only update if deadline is provided
            try:
                reminder.time = datetime.strptime(reminder.time, "%Y-%m-%d %H:%M:%S")
            except ValueError:
             return jsonify({"message": "Invalid deadline format. Use YYYY-MM-DD HH:MM:SS."}), 400



        db.session.commit()
        return  jsonify({"message": "Reminder Updated!"}), 200

#delete task   
@app.route("/tasks/delete/<int:task_id>", methods=["DELETE"])
@app.route("/delete_task/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
        task = Task.query.get(task_id)
        if not task:
            return  jsonify({"message": "Task Not Found!"}), 404
        
        db.session.delete(task)
        db.session.commit()
        return  jsonify({"message": "Task Deleted!"}), 200

#delete reminder  
@app.route("/reminders/delete/<int:reminder_id>", methods=["DELETE"])
@app.route("/delete_reminder/<int:reminder_id>", methods=["DELETE"])
def delete_reminder(reminder_id):
        reminder = Reminder.query.get(reminder_id)
        if not reminder:
            return  jsonify({"message": "Reminder Not Found!"}), 404
        
        db.session.delete(reminder)
        db.session.commit()
        return  jsonify({"message": "Reminder Deleted!"}), 200


if __name__ == '__main__':
   
   
   with app.app_context():
        db.create_all()
   app.run(debug=True, host="127.0.0.1", port=5000)