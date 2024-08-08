from datetime import datetime

from django.shortcuts import render
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from paypal.standard.ipn.signals import valid_ipn_received
from paypal.standard.models import ST_PP_COMPLETED

from donate.forms import DonateClientForm
from donate.models import DonateClient
from paypal_int.settings import PAYPAL_RECEIVER_EMAIL


# Create your views here.
def home(request):
    if request.method == 'POST':
        form = DonateClientForm(request.POST)
        if form.is_valid():
            capture_time = datetime.now().strftime("%Y%m%d%H%M%S")
            amount = form.cleaned_data['amount']
            payer_info = {
                "name": form.cleaned_data['name'],
                "email": form.cleaned_data['email'],
                "amount": str(amount),
                "invoice_id": capture_time,
            }
            request.session['payer_info'] = payer_info
            notify_url = request.build_absolute_uri(reverse('paypal-ipn'))
            return_url = request.build_absolute_uri(reverse('payment_done'))
            cancel_url = request.build_absolute_uri(reverse('payment_cancelled'))

            paypal_dict = {
                "business": PAYPAL_RECEIVER_EMAIL,
                "amount": str(amount),
                "item_name": "Church Donation",
                "invoice": capture_time,
                "currency_code": "CAD",
                "notify_url": notify_url,
                "return_url": return_url,
                "cancel_url": cancel_url,
            }
            form = PayPalPaymentsForm(initial=paypal_dict, button_type="donate")
            return render(request, "donate/process_payment.html",
                          {"form": form, "payer_info": payer_info})
        else:
            return render(request, 'donate/home.html', {
                'form': form,
            })
    else:
        form = DonateClientForm()

    return render(request, 'donate/home.html', {
        'form': form,
    })


def payment_done(request):
    payer_info = request.session.get('payer_info')
    if payer_info:
        donate_client = DonateClient.objects.create(
            name=payer_info['name'],
            email=payer_info['email'],
            amount=payer_info['amount'],
            invoice_id=payer_info['invoice_id'],
        )
        donate_client.save()
        del request.session['payer_info']
    return render(request, 'donate/payment_done.html')


def payment_cancelled(request):
    return render(request, 'donate/payment_cancelled.html')


def payment_notification(sender, **kwargs):
    ipn_obj = sender

    # retrieve the donateclient object where the invoice_id is equal to the ipn_obj.invoice
    donate_client = DonateClient.objects.get(invoice_id=ipn_obj.invoice)

    # check if the payment status is completed, the amount is the same as the amount in the donateclient object,
    # the receiver email is the same as the paypal receiver email
    # if not about detected_errors field with the errors observed
    if donate_client is None:
        # todo: log the error
        return

    if (ipn_obj.payment_status == ST_PP_COMPLETED and
            ipn_obj.mc_gross == donate_client.amount and
            ipn_obj.receiver_email == PAYPAL_RECEIVER_EMAIL):
        donate_client.status = "Complete"
        donate_client.save()
    else:
        donate_client.detected_errors = f"Payment status: {ipn_obj.payment_status}, Amount: {ipn_obj.mc_gross}, Receiver email: {ipn_obj.receiver_email}"
        donate_client.save()


valid_ipn_received.connect(payment_notification)
