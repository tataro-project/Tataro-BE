import hashlib
import hmac
import time
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from .forms import PaymentForm
from .models import Payment
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Replace with your actual merchant ID and key (from settings or env vars!)
MERCHANT_ID = "your_merchant_id"  # Replace
MERCHANT_KEY = "your_merchant_key"  # Replace
KORPAY_API_URL = "https://pgapi.korpay.com/payInit_hash.korpay" # Replace

def generate_hash(merchant_id, edi_date, price, merchant_key):
    hash_string = merchant_id + edi_date + str(price) + merchant_key
    hashed = hashlib.sha256(hash_string.encode('utf-8')).hexdigest()
    return hashed

class PaymentRequestView(View):
    template_name = 'payment/payment_request.html'

    def get(self, request):
        form = PaymentForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = PaymentForm(request.POST)
        if form.is_valid():
            # Extract data from the form
            goods_name = form.cleaned_data['goods_name']
            price = form.cleaned_data['price']
            buyer_name = form.cleaned_data['buyer_name']
            buyer_tel = form.cleaned_data['buyer_tel']
            buyer_email = form.cleaned_data['buyer_email']
            moid = form.cleaned_data['moid']

            # Generate edi_date and hash
            edi_date = time.strftime("%Y%m%d%H%M%S")
            hash_str = generate_hash(MERCHANT_ID, edi_date, price, MERCHANT_KEY)

            # Create a Payment object (but don't save yet)
            payment = Payment(
                merchant_id=MERCHANT_ID,
                goods_name=goods_name,
                price=price,
                buyer_name=buyer_name,
                buyer_tel=buyer_tel,
                buyer_email=buyer_email,
                moid=moid,
                return_url=request.build_absolute_uri(reverse('payment:payment_response')), # Important: Full URL
                edi_date=edi_date,
                hash_str=hash_str
            )

            # Prepare the context for the Korpay form submission
            context = {
                'form': form,
                'merchant_id': MERCHANT_ID,
                'goods_name': goods_name,
                'price': price,
                'buyer_name': buyer_name,
                'buyer_tel': buyer_tel,
                'buyer_email': buyer_email,
                'moid': moid,
                'return_url': payment.return_url,
                'edi_date': edi_date,
                'hash_str': hash_str,
                'korpay_api_url': KORPAY_API_URL,
            }
            request.session['payment_data'] = {
                'merchant_id': MERCHANT_ID,
                'goods_name': goods_name,
                'price': str(price),
                'buyer_name': buyer_name,
                'buyer_tel': buyer_tel,
                'buyer_email': buyer_email,
                'moid': moid,
                'return_url': payment.return_url,
                'edi_date': edi_date,
                'hash_str': hash_str
            }

            return render(request, 'payment/payment_submit.html', context)
        else:
            return render(request, self.template_name, {'form': form})

@method_decorator(csrf_exempt, name='dispatch')
class PaymentResponseView(View):
    template_name = 'payment/payment_response.html'

    def post(self, request):
        payment_data = request.session.get('payment_data')

        if not payment_data:
            return HttpResponse("Payment data not found in session.", status=400)

        result_code = request.POST.get('resultCd')
        result_msg = request.POST.get('resultMsg')
        tid = request.POST.get('tid')
        app_no = request.POST.get('appNo')
        card_no = request.POST.get('cardNo')
        pay_method = request.POST.get('payMethod')

        payment = Payment(**payment_data)
        payment.result_code = result_code
        payment.result_msg = result_msg
        payment.tid = tid
        payment.app_no = app_no
        payment.card_no = card_no
        payment.pay_method = pay_method
        payment.save()

        context = {
            'result_code': result_code,
            'result_msg': result_msg,
            'tid': tid,
            'app_no': app_no,
            'card_no': card_no,
            'pay_method':pay_method,
            'payment': payment
        }
        return render(request, self.template_name, context)
