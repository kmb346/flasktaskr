# test_tasks.py


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
        return self.app.get('/users/logout/', follow_redirects=True)
		


	
    ###############
	#### tests ####
	###############

    def test_form_is_present_on_login_page(self):
        response = self.app.get('/users/')
        self.assertEquals(response.status_code, 200)
        self.assertIn('Please sign in to access your task list',
            response.data)
			
    def test_users_can_register(self):
        new_user = User("mherman", "michael@herman.org",
            "michaelherman")
        db.session.add(new_user)
        db.session.commit()
        test = db.session.query(User).all()
        for t in test:
            t.name
        assert t.name == "mherman"    
	
    def test_users_cannot_login_unless_registered(self):
        response  = self.login('foo', 'bar')
        self.assertIn('Invalid username or password.', response.data)
		
    def test_users_can_login(self):
        self.register()
        response = self.login('Fletcher', 'python101')
        self.assertIn('You are logged in. Enjoy!', response.data)

    def test_logged_in_users_can_logout(self):
        self.register()
        self.login('Fletcher', 'python101')
        response = self.logout()
        self.assertIn('You are logged out. Bye. :(', response.data)

    def test_not_logged_in_users_cannot_logout(self):
        response = self.logout()
        self.assertNotIn('You are logged out. Bye. :(', response.data)
		
    def test_form_is_present_on_register_page(self):
        response = self.app.get('/users/register/')
        self.assertEquals(response.status_code, 200)
        self.assertIn('Please register to start a task list',
            response.data)    
		
    def test_user_registration(self):
        self.app.get('/users/register/', follow_redirects=True)
        response = self.register()
        self.assertIn('Thanks for registering. Please login.', response.data)

    def test_invalid_form_data(self):
        self.register()
        response = self.login('alert("alert box!");', 'foo')
        self.assertIn('Invalid username or password.', response.data)    
	
    def test_user_registration_field_errors(self):
        response = self.app.post('/users/register/', data=dict(
            name='Fletcher', 
            email='fletcher@realpython.com',
            password='python101', 
            confirm=''), follow_redirects=True)
        self.assertIn(
            'This field is required.', response.data)
           
    def test_duplicate_user_registration_throws_error(self):
        self.register()
        response = self.register()
        self.assertIn(
            'Oh no! That username and/or email already exist. Please try again.', 
                response.data)
			
    def test_default_user_role(self):
        db.session.add(
            User(
                "Johnny",
                "john@doe.com",
                "johnny"
            )
        )
        db.session.commit
        users = db.session.query(User).all()
        print users
        for user in users:
            self.assertEquals(user.role, 'user')
		
    def test_users_cannot_see_task_modify_links_for_tasks_not_created_by_them(self):
        self.create_user()
        self.login('Michael', 'python')
        self.app.get('/tasks/tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.register()
        response = self.login('Fletcher', 'python101')
        self.app.get('/tasks/tasks/', follow_redirects=True)
        self.assertNotIn('Mark as complete', response.data)
        self.assertNotIn('Delete', response.data)
		
    def test_users_can_see_modify_links_for_tasks_created_by_them(self):
        self.create_user()
        self.login('Michael', 'python')
        self.app.get('/tasks/tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.register()
        self.login('Fletcher', 'python101')
        self.app.get('/tasks/tasks/', follow_redirects=True)
        response = self.create_task()
        self.assertIn('/tasks/complete/2/', response.data)
        self.assertIn('/tasks/delete/2/', response.data) 
		
    def test_admin_users_can_see_modify_links_for_all_tasks(self):
        self.create_user()
        self.login('Michael', 'python')
        self.app.get('/tasks/tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_admin_user()
        self.login('Superman', 'allpowerful')
        self.app.get('/tasks/tasks/', follow_redirects=True)
        response = self.create_task()
        self.assertIn('/tasks/complete/1/', response.data)
        self.assertIn('/tasks/delete/1/', response.data) 
		
        	
	
if __name__ == '__main__':
    unittest.main()