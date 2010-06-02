from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from lunch.forms import OrderForm
from lunch.models import Order

import datetime

@login_required
def placeOrder(request):
    username = request.session['username']
    if request.method == 'POST': # If the form has been submitted...
        form = OrderForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            form.save()
            return HttpResponseRedirect('/lunch/thanks') # Redirect after POST
    else:
        f = OrderForm() # An unbound form
        new_order = f.save(commit=False)
        new_order.username = 'bmbouter'
        form = OrderForm(instance=new_order) # The username in the form

    return HttpResponse(username)

    return render_to_response('orderform.html',
                            {'formset': form,
                             'username' : username },
                            context_instance=RequestContext(request))

def thanks(request):
    return HttpResponse('Thanks for the order!')

def viewOrders(request, date=datetime.date.today()):
    orders = Order.objects.filter(date=date)
    total = reduce(lambda x,y: 1,orders,0)
    return render_to_response('vieworders.html',{'orders':orders, 'total':total})
