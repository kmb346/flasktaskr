# db_create.py


from views import db
from models import Task
from datetime import date

# create the database and the db table
db.create_all()

#insert database
#db.session.add(Task("Finish this tutorial", date(2014, 12, 31), 10, 1))
#db.session.add(Task("Finish Real Python", date(2014, 12, 31), 10, 1))

# commit the changes
db.session.commit()

