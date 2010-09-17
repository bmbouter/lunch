from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse as urlreverse
from django.contrib.auth import logout as django_logout

from lunch.forms import OrderForm
from lunch.models import Order

import datetime
import calendar

@login_required
def placeOrder(request):
    sameday = False
    # if lunch was already submitted today...
    todays_orders = Order.objects.filter(user=request.user,date=datetime.date.today())
    if todays_orders.exists():
        sameday = True
    
    if request.method == 'POST' and not sameday: # If the form has been submitted...
        form = OrderForm(request.POST, instance=Order(user=request.user)) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            form.save()
            return HttpResponseRedirect('/lunch/thanks/') # Redirect after POST
    else:
        form = OrderForm() # An unbound form

    return render_to_response('orderform.html',
                               {'form': form, 'username' : request.user.username, 'sameday': sameday },
                              context_instance=RequestContext(request))

def thanks(request):
    return HttpResponse('Thanks for the order!')

def viewOrders(request, date=None):
    if date=='today':  date = datetime.date.today()
    if date:
        orders = Order.objects.filter(date=date)
    else:
        orders = Order.objects.all()
    total = reduce(lambda x,y: 1,orders,0)
    return render_to_response('vieworders.html',{'orders':orders, 'total':total})


def viewOrdersSummary(request, year=None, month=None):
    year = int(year)  if year is not None else  datetime.date.today().year
    month = int(month)  if month is not None else  datetime.date.today().month
    
    # get all months & years in the db
    values_list = Order.objects.values_list('date', flat=True)
    unique_dates = set(
        val.replace(day=1) for val in values_list if isinstance(val, datetime.date)
        )
    # also include the current month
    unique_dates.add(datetime.date.today().replace(day=1))
    unique_dates = list(unique_dates)
    unique_dates.sort(reverse=True)
    
    # date info to pass to html template
    dateslist = list(
                {'title': d.strftime('%b %Y'), 
                 'val': urlreverse('lunch-summary-view', kwargs={'year':d.year,'month':d.month}), 
                 'selected': d.month==month and d.year==year} 
            for d in unique_dates)
    
    # orders for given month and year
    orders = Order.objects.filter(date__year=year,date__month=month)
    
    usertotals = []
    grandtotal = sum((ord.guests+1) for ord in orders)
    
    for user in User.objects.all():
        uorders = orders.filter(user=user)
        usertotal = {}
        usertotal['user'] = user
        t = sum((ord.guests+1) for ord in uorders)
        usertotal['sum'] = t
        usertotal['percent'] = 0.  if grandtotal==0 else  100.*t/float(grandtotal)
        usertotals.append(usertotal)
    
    return render_to_response('orders_summary.html',
                             {'usertotals':usertotals, 'month':calendar.month_name[month], 
                              'year':year, 'grandtotal':grandtotal,
                              'dateslist':dateslist}
                             )
    
def logout(request):
    django_logout(request)
    return HttpResponse('Logout successful.')
    
    
    
    
    
    
    
