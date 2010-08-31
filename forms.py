from django.forms import ModelForm
from lunch.models import Order

class OrderForm(ModelForm):
    class Meta:
        model = Order
        exclude = ['user','date']
