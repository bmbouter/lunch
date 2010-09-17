
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse as urlreverse

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
            url = urlreverse('lunch-placeorder-view')
            response = self.client.get(url)
            self.assertEquals(response.status_code, 200)
            self.assertEquals(response.context['user'], self.users[0])
            
    def test_postBasic(self):
        with self.scoped_login('user0', 'password'):
            data = {'guests':0, 'user':self.users[0], 'date':datetime.date.today()}
            url = urlreverse('lunch-placeorder-view')
            response = self.client.post(url, data)
            
            self.assertEquals(response.status_code, 200)
            
            self.assertEquals(Order.objects.all().count(),1)
            order = Order.objects.all()[0]
            
            self.assertEquals(order.date, datetime.date.today())
            self.assertEquals(order.user, self.users[0])
            self.assertEquals(order.guests, 0)
            

class OrdersSummary_basic_TestCase(Lunch_TestCaseBase):
    def test_noOrders(self):
        url = urlreverse('lunch-summarytoday-view')
        response = self.client.get(url)
        
        self.assertEquals(response.status_code, 200)
        
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
                for i in range(nusers,7)
            ]
        # add orders for this month
        y = self.today.year
        m = self.today.month
        lastmonth = (self.today.replace(day=1) - datetime.timedelta(days=1))
        nextmonth = (self.today.replace(day=1) + datetime.timedelta(days=31)).replace(day=1)
        
        self.lastmonth = lastmonth
        self.nextmonth = nextmonth
        
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
        
        # user5  tot: 5
        Order(date=D(y,m,7), user=U[5], guests=1).save()
        Order(date=D(y,m,8), user=U[5], guests=1).save()
        Order(date=D(y,m,9), user=U[5], guests=0).save()
        
        # user6  tot: 3
        Order(date=D(y,m,7), user=U[6], guests=0).save()
        Order(date=D(y,m,8), user=U[6], guests=1).save()
            
    def test_withOrders(self):
        url = urlreverse('lunch-summarytoday-view')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        
        self.assertEquals(response.context['grandtotal'], 20)
        self.assertEquals(response.context['year'], self.today.year)
        self.assertEquals(response.context['month'], calendar.month_name[self.today.month])
        
        usertotals = response.context['usertotals']
        usertotals = dict((utot['user'].username,utot) for utot in usertotals)
        
        self.assertEquals(usertotals['user0']['sum'], 3)
        self.assertEquals(usertotals['user1']['sum'], 9)
        self.assertEquals(usertotals['user2']['sum'], 0)
        self.assertEquals(usertotals['user3']['sum'], 0)
        self.assertEquals(usertotals['user4']['sum'], 0)
        self.assertEquals(usertotals['user5']['sum'], 5)
        self.assertEquals(usertotals['user6']['sum'], 3)
            
        self.assertAlmostEqual(usertotals['user0']['percent'], 15.)
        self.assertAlmostEqual(usertotals['user1']['percent'], 45.)
        self.assertAlmostEqual(usertotals['user2']['percent'], 0)
        self.assertAlmostEqual(usertotals['user3']['percent'], 0)
        self.assertAlmostEqual(usertotals['user4']['percent'], 0)
        self.assertAlmostEqual(usertotals['user5']['percent'], 25.)
        self.assertAlmostEqual(usertotals['user6']['percent'], 15.)
        
    def test_datesList(self):
        today = self.today
        nextmonth = self.nextmonth
        lastmonth = self.lastmonth
        
        url = urlreverse('lunch-summarytoday-view')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        
        dateslist = response.context['dateslist']
        self.assertEquals(len(dateslist),3)
        self.assertEquals(
            dateslist[0]['val'], 
            urlreverse('lunch-summary-view', kwargs={'year':nextmonth.year,'month':nextmonth.month})
            )
        self.assertEquals(
            dateslist[1]['val'], 
            urlreverse('lunch-summary-view', kwargs={'year':today.year,'month':today.month})
            )
        self.assertEquals(
            dateslist[2]['val'], 
            urlreverse('lunch-summary-view', kwargs={'year':lastmonth.year,'month':lastmonth.month})
            )
            
    def test_selectedOption(self):
        # This test assumes that the 'dateslist' has the dates in descending order.
        
        today = self.today
        nextmonth = self.nextmonth
        lastmonth = self.lastmonth
        
        url = urlreverse('lunch-summarytoday-view')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        
        dateslist = response.context['dateslist']
        self.assertEquals(len(dateslist),3)
        self.assertEquals(dateslist[0]['selected'],False)
        self.assertEquals(dateslist[1]['selected'],True) # This month
        self.assertEquals(dateslist[2]['selected'],False)
        
        
        url = urlreverse('lunch-summary-view', kwargs={'year':today.year,'month':today.month})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        
        dateslist = response.context['dateslist']
        self.assertEquals(len(dateslist),3)
        self.assertEquals(dateslist[0]['selected'],False)
        self.assertEquals(dateslist[1]['selected'],True) # This month
        self.assertEquals(dateslist[2]['selected'],False)
        
        
        url = urlreverse('lunch-summary-view', kwargs={'year':nextmonth.year,'month':nextmonth.month})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        
        dateslist = response.context['dateslist']
        self.assertEquals(len(dateslist),3)
        self.assertEquals(dateslist[0]['selected'],True)
        self.assertEquals(dateslist[1]['selected'],False) # This month
        self.assertEquals(dateslist[2]['selected'],False)
        
        
        url = urlreverse('lunch-summary-view', kwargs={'year':lastmonth.year,'month':lastmonth.month})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        
        dateslist = response.context['dateslist']
        self.assertEquals(len(dateslist),3)
        self.assertEquals(dateslist[0]['selected'],False)
        self.assertEquals(dateslist[1]['selected'],False) # This month
        self.assertEquals(dateslist[2]['selected'],True)
        
            


#==============================================================================#
def suite():
    test_suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    test_suite.addTest(loader.loadTestsFromTestCase(PlaceOrder_TestCase))
    test_suite.addTest(loader.loadTestsFromTestCase(OrdersSummary_basic_TestCase))
    test_suite.addTest(loader.loadTestsFromTestCase(OrdersSummary_TestCase))
    return test_suite
