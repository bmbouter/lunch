from django.conf.urls.defaults import *

import datetime

urlpatterns = patterns('lunch',
    (r'^order/$', 'views.placeOrder'),
    (r'^$', 'views.placeOrder'),
    (r'^thanks/$', 'views.thanks'),
    (r'^orders/$', 'views.viewOrders'),
    (r'^orders/today/$', 'views.viewOrders', {'date':datetime.date.today()}),
    (r'^orders/(?P<date>(\d{4}-\d{2}-\d{2}){1})/$', 'views.viewOrders'),
    (r'^summary/$', 'views.viewOrdersSummary' ),
    (r'^summary/(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'views.viewOrdersSummary', {}, 'lunch-summary-view'),
)
