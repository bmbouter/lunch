from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

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
    if date:
        orders = Order.objects.filter(date=date)
    else:
        orders = Order.objects.all()
    total = reduce(lambda x,y: 1,orders,0)
    return render_to_response('vieworders.html',{'orders':orders, 'total':total})


def viewOrdersSummary(request, year=None, month=None):
    if not year:
        year = datetime.date.today().year
    if not month:
        month = datetime.date.today().month
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
                              'year':year, 'grandtotal':grandtotal}
                             )
