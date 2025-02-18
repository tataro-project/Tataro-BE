from django import forms

class PaymentForm(forms.Form):
    goods_name = forms.CharField(label="Product Name", max_length=100)
    price = forms.DecimalField(label="Price")
    buyer_name = forms.CharField(label="Buyer Name", max_length=100)
    buyer_tel = forms.CharField(label="Buyer Phone", max_length=20)
    buyer_email = forms.EmailField(label="Buyer Email")
    moid = forms.CharField(label="Order ID", max_length=40)
