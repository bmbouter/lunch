from django.conf.urls.defaults import *

import datetime

urlpatterns = patterns('lunch',
    (r'^order/$', 'views.placeOrder', {},       'lunch-placeorder-view'),
    (r'^$', 'views.placeOrder'),
    (r'^thanks/$', 'views.thanks', {},          'lunch-thanks-view'),
    (r'^orders/$', 'views.viewOrders', {},      'lunch-orders-view'),
    (r'^orders/today/$', 'views.viewOrders', {'date': 'today'},                         'lunch-orderstoday-view'),
    (r'^orders/(?P<date>(\d{4}-\d{2}-\d{2}){1})/$', 'views.viewOrders', {},             'lunch-ordersondate-view'),
    (r'^summary/$', 'views.viewOrdersSummary', {},                                      'lunch-summarytoday-view'),
    (r'^summary/(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'views.viewOrdersSummary', {},   'lunch-summary-view'),
)