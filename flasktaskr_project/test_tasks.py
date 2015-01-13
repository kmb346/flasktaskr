# test_users.py


import os
import unittest

from project import app, db
from config import basedir
from project.models import Task, User

TEST_DB = 'test.db'


class AllTests(unittest.TestCase):

    ############################
    #### setup and teardown ####
    ############################
	
    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED']  = False
        app.config['SQLALCHEMY_DATABASE_URI']  = 'sqlite:///' + \
            os.path.join(basedir, TEST_DB)
        self.app = app.test_client()
        db.create_all()
    
    # executed after each test	
    def tearDown(self):
        db.drop_all()
		
    ##########################
	#### helper functions ####
	##########################
	
    def create_user(self):
        new_user = User(
            name='Michael',
            email='michael@realpython.com',
            password='python'
        )
        db.session.add(new_user)
        db.session.commit()
  
    def create_admin_user(self):
        new_user = User(
            name='Superman',
            email='admin@realpython.com',
            password='allpowerful',
            role='admin'
        )
        db.session.add(new_user)
        db.session.commit()
		
    def create_task(self):
        return self.app.post('/tasks/add/', data=dict(
            name='Go to the bank',
            due_date='02/05/2014',
            priority='1',
            posted_date='02/04/2014',
            status='1'
        ), follow_redirects=True)
		
    def register(self):
        return self.app.post('/users/register/', data=dict(
            name='Fletcher', 
            email='fletcher@realpython.com',
            password='python101',
            confirm='python101'), follow_redirects=True)

    def login(self, name, password):
        return self.app.post('/users/', data=dict(
            name=name, password=password), follow_redirects=True)
			
    def logout(self):
        return self.app.get('/logout/', follow_redirects=True)
		
	
	###############
	#### tests ####
	###############
	

    def test_users_can_add_tasks(self):
        self.register()
        self.login('Fletcher', 'python101')
        self.app.get('/tasks/tasks/', follow_redirects=True)
        response = self.create_task()
        self.assertIn('New entry was successfully posted. Thanks.', response.data)

    def test_users_cannot_add_tasks_when_error(self):
        self.register()
        self.login('Fletcher', 'python101')
        self.app.get('/tasks/tasks/', follow_redirects=True)
        response = self.app.post('/tasks/add/', data=dict(
            name='Go to the bank',
            due_date='',
            priority='1',
            posted_date='02/05/2014',
            status='1'
        ), follow_redirects=True)
        self.assertIn('This field is required.', response.data)

    def test_users_can_complete_tasks(self):
        self.register()
        self.login('Fletcher', 'python101')
        self.app.get('/tasks/tasks/', follow_redirects=True)
        self.create_task()
        response = self.app.get("/tasks/complete/1/", follow_redirects=True)
        self.assertIn('The task was marked as complete.',
            response.data)
			
    def test_users_can_delete_tasks(self):
        self.register()
        self.login('Fletcher', 'python101')
        self.app.get('/tasks/tasks/', follow_redirects=True)
        self.create_task()
        response = self.app.get("/tasks/delete/1/", follow_redirects=True)
        self.assertIn('The task was deleted. Why not add another one?', response.data)
    
    def test_users_cannot_complete_tasks_not_created_by_them(self):
        self.register()
        self.login('Fletcher', 'python101')
        self.app.get('/tasks/tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_user()
        self.login('Michael', 'python')
        self.app.get('/tasks/tasks/', follow_redirects=True)
        response = self.app.get("/tasks/complete/1/", follow_redirects=True)
        self.assertIn('You can only update tasks that belong to you.', 
            response.data)
			
    def test_users_cannot_delete_tasks_not_created_by_them(self):
        self.register()
        self.login('Fletcher', 'python101')
        self.app.get('/tasks/tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_user()
        self.login('Michael', 'python')
        self.app.get('/tasks/tasks/', follow_redirects=True)
        response = self.app.get("/tasks/delete/1/", follow_redirects=True)
        self.assertIn('You can only delete tasks that belong to you.', 
            response.data)
    
    def test_admin_users_can_complete_tasks_that_are_not_created_by_them(self):
        self.create_user()
        self.login('Michael', 'python')
        self.app.get('/tasks/tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_admin_user()
        self.login('Superman', 'allpowerful')
        self.app.get('/tasks/tasks/', follow_redirects=True)
        response = self.app.get("/tasks/complete/1/", follow_redirects=True)
        self.assertNotIn(
            'You can only update tasks that belong to you.', response.data)

    def test_admin_users_can_delete_tasks_that_are_not_created_by_them(self):
        self.create_user()
        self.login('Michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_admin_user()
        self.login('Superman', 'allpowerful')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get("/tasks/delete/1/", follow_redirects=True)
        self.assertNotIn(
            'You can only update tasks that belong to you.', response.data)
			
    def test_task_template_displays_logged_in_username(self):
        self.register()
        self.login('Fletcher', 'python101')
        response = self.app.get('/tasks/tasks/', follow_redirects=True)
        self.assertIn('Fletcher', response.data)
	
if __name__ == '__main__':
    unittest.main() 