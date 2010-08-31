
from django.test import TestCase
from django.contrib.auth.models import User

from models import Order

import datetime
import unittest

#==============================================================================#
class UserLogin_Context(object):
    def __init__(self, client, username, password):
        self.client = client
        self.username = username
        self.password = password
    def __enter__(self):
        self.client.login(username=self.username, password=self.password)
    def __exit__(self, type, value, traceback):
        self.client.logout()
        
#==============================================================================#
class Lunch_TestCaseBase(TestCase):
    def scoped_login(self, username, password):
        return UserLogin_Context(self.client, username, password)
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", email="", password="password")
        self.user2 = User.objects.create_user(username="user2", email="", password="password")
    def tearDown(self):
        Order.objects.all().delete()
        self.user1.delete()
        self.user2.delete()
    

#==============================================================================#
class PlaceOrder_Test(Lunch_TestCaseBase):
    def test_basic(self):
        with self.scoped_login('user1', 'password'):
            response = self.client.get('/lunch/order/')
            self.assertEquals(response.context['user'],self.user1)
            
    def test_postBasic(self):
        with self.scoped_login('user1', 'password'):
            data = {'guests':0, 'user':self.user1, 'date':datetime.date.today()}
            response = self.client.post('/lunch/order/', data)
            
            self.assertEquals(Order.objects.all().count(),1)
            order = Order.objects.all()[0]
            
            self.assertEquals(order.date, datetime.date.today())
            self.assertEquals(order.user, self.user1)
            self.assertEquals(order.guests, 0)


#==============================================================================#
def suite():
    test_suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    test_suite.addTest(loader.loadTestsFromTestCase(PlaceOrder_Test))
    return test_suite
