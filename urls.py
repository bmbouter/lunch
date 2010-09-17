from django.conf.urls.defaults import *
#from django.contrib.auth.views import logout_then_login
#import django.contrib.auth.views

import datetime

urlpatterns = patterns('lunch',
    (r'^order/$', 'views.placeOrder'),
    (r'^$', 'views.placeOrder'),
    #(r'^logout/$', django.contrib.auth.views.logout_then_login),
    (r'^logout/$', 'views.logout'),
    (r'^thanks/$', 'views.thanks'),
    (r'^orders/$', 'views.viewOrders'),
    (r'^orders/today/$', 'views.viewOrders', {'date': 'today'}),
    (r'^orders/(?P<date>(\d{4}-\d{2}-\d{2}){1})/$', 'views.viewOrders'),
    (r'^summary/$', 'views.viewOrdersSummary' ),
    (r'^summary/(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'views.viewOrdersSummary', {}, 'lunch-summary-view'),
)
