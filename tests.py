
from django.test import TestCase
from django.contrib.auth.models import User

from models import Order

import datetime
import calendar
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
        self.today = datetime.date.today()
        self.users = [
                User.objects.create_user(
                    username="user%d"%i,
                    email="", 
                    password="password") 
                for i in range(2)
            ]
        #self.user1 = User.objects.create_user(username="user1", email="", password="password")
        #self.user2 = User.objects.create_user(username="user2", email="", password="password")
    def tearDown(self):
        Order.objects.all().delete()
        for user in self.users:
            user.delete()
    

#==============================================================================#
class PlaceOrder_TestCase(Lunch_TestCaseBase):
    def test_basic(self):
        with self.scoped_login('user0', 'password'):
            response = self.client.get('/lunch/order/')
            self.assertEquals(response.context['user'],self.users[0])
            
    def test_postBasic(self):
        with self.scoped_login('user0', 'password'):
            data = {'guests':0, 'user':self.users[0], 'date':datetime.date.today()}
            response = self.client.post('/lunch/order/', data)
            
            self.assertEquals(Order.objects.all().count(),1)
            order = Order.objects.all()[0]
            
            self.assertEquals(order.date, datetime.date.today())
            self.assertEquals(order.user, self.users[0])
            self.assertEquals(order.guests, 0)
            

class OrdersSummary_basic_TestCase(Lunch_TestCaseBase):
    def test_noOrders(self):
        response = self.client.get('/lunch/summary/')
        
        self.assertEquals(response.context['grandtotal'], 0)
        self.assertEquals(response.context['year'], self.today.year)
        self.assertEquals(response.context['month'], calendar.month_name[self.today.month])
        
        usertotals = response.context['usertotals']
        for usertotal in usertotals:
            self.assertEquals(usertotal['sum'], 0)
            self.assertEquals(usertotal['percent'], 0)
    
        
class OrdersSummary_TestCase(Lunch_TestCaseBase):
    def setUp(self):
        super(OrdersSummary_TestCase,self).setUp()
        # add some extra users
        nusers = len(self.users)
        self.users = self.users + [
                User.objects.create_user(
                    username="user%d"%i,
                    email="", 
                    password="password") 
                for i in range(nusers,5)
            ]
        # add orders for this month
        y = self.today.year
        m = self.today.month
        lastmonth = (self.today.replace(day=1) - datetime.timedelta(days=1))
        nextmonth = (self.today.replace(day=1) + datetime.timedelta(days=31)).replace(day=1)
        
        D = datetime.date
        U = self.users
        
        # user0  tot: 3
        Order(date=D(y,m,1), user=U[0], guests=0).save()
        Order(date=D(y,m,2), user=U[0], guests=0).save()
        Order(date=D(y,m,3), user=U[0], guests=0).save()
        
        # user1  tot: 9
        Order(date=D(y,m,1), user=U[1], guests=1).save()
        Order(date=D(y,m,2), user=U[1], guests=2).save()
        Order(date=D(y,m,3), user=U[1], guests=3).save()
        
        # user2  tot: 3 (but previous month)
        Order(date=D(lastmonth.year,lastmonth.month,1), user=U[2], guests=1).save()
        Order(date=D(lastmonth.year,lastmonth.month,2), user=U[2], guests=0).save()
        
        # user3  tot: 3 (but next month)
        Order(date=D(nextmonth.year,nextmonth.month,1), user=U[3], guests=1).save()
        Order(date=D(nextmonth.year,nextmonth.month,2), user=U[3], guests=0).save()
        
        # user4  tot: 0 (not entered on purpose)
        
        # TODO:...
            
    def test_withOrders(self):
        response = self.client.get('/lunch/summary/')
        
        self.assertEquals(response.context['grandtotal'], 12)
        
        # TODO...


#==============================================================================#
def suite():
    test_suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    test_suite.addTest(loader.loadTestsFromTestCase(PlaceOrder_TestCase))
    test_suite.addTest(loader.loadTestsFromTestCase(OrdersSummary_basic_TestCase))
    test_suite.addTest(loader.loadTestsFromTestCase(OrdersSummary_TestCase))
    return test_suite
