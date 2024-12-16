from config import db 

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(15), nullable=False)
    priority = db.Column(db.String(10), default="Medium")
    deadline = db.Column(db.DateTime, nullable=False)


    @property
    def to_json(self):
        return{
            "id": self.id,
            "name": self.name,
            "priority": self.priority,          
            "deadline": self.deadline,
        }
    

class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(15), nullable=False)
    priority = db.Column(db.String(10), default="Medium")
    time = db.Column(db.DateTime, nullable=False)
    
    @property
    def to_json(self):
        return{

            "id": self.id,
            "name": self.name,
            "priority": self.priority, 
            "category": self.category,
            "time": self.time,
            
            
        }
    
 

