from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from lunch.forms import OrderForm
from lunch.models import Order

import datetime

@login_required
def placeOrder(request):
    sameday = False
    # TODO: if lunch was already submitted today...
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

def viewOrders(request, date=datetime.date.today()):
    orders = Order.objects.filter(date=date)
    total = reduce(lambda x,y: 1,orders,0)
    return render_to_response('vieworders.html',{'orders':orders, 'total':total})
