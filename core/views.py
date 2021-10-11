from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from .models import Item, OrderItem, Order, BillingAddress
from django.views.generic import ListView, DetailView, View
from.forms import CheckoutForm


def item_list(request):
    context = {'items': Item.objects.all()}
    return render(request, 'home_page.html', context)


class CheckoutView(View):

    def get(self,*args,**kwargs):
        form = CheckoutForm()
        context = {'form': form}
        return render(self.request, 'checkout-page.html', context)

    def post(self,*args,**kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm(self.request.POST)
            print(self.request.POST)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                # TODO : add functionality for these fields
                # same_shipping_address = form.cleaned_data.get('same_shipping_address')
                # save_info = form.cleaned_data.ge
                # t('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                # TODO :add a redirect to the selected payment option
                print(form.cleaned_data)
                print('print the form is valid')
                return redirect('core:checkout')
            messages.warning(self.request, 'Failed checkout')
            return redirect('core:checkout')


        except ObjectDoesNotExist:
            messages.error(self.request, 'You do not have an active order')
            return redirect('core:home_page')


class PaymentView(View):
    def get(self,*args,**kwargs):
        return render(self.request,'payment.html')



class HomeView(ListView):
    model = Item
    template_name = 'home_page.html'
    context_object_name = 'items'
    paginate_by = 10


class OrderSummaryView(LoginRequiredMixin,View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context={
                'order':order
            }
        except ObjectDoesNotExist:
            messages.error(self.request, 'You do not have an active order')
            return redirect('core:home_page')
        return render(self.request, 'order_summary.html',context )


class ItemDetailView(DetailView):
    model = Item
    template_name = 'product.html'


""" this add to cart i am using it to add itmes to the cart first i get the items 
 in the first line second i create the item in the orderitem the middle then 
 then i check if the item have being ordered before running if statement still
 confused"""


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(item=item
                                                          , user=request.user,
                                                          ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    """ check if the order queryset exist before doing anything and 
    if the order is not completed"""
    if order_qs.exists():
        order = order_qs[0]
        """check if the order item is in the order"""
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity updated .")
            return redirect('core:order_summary')

        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect('core:order_summary')

    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item quantity updated .")
        return redirect('core:order_summary')

@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    """ check if the order queryset exist before doing anything"""
    if order_qs.exists():
        order = order_qs[0]
        """check if the order item is in the order"""
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item,
                                                  user=request.user,
                                                  ordered=False)[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart.")
            return redirect('core:order_summary')
        else:
            messages.info(request, "This item was not in your cart")
            return redirect('core:order_summary', slug=slug)
    else:
        # message the user doesnt have an other
        messages.info(request, "You do not have an active order")
        return redirect('core:product', slug=slug)
    # return redirect('core:product', slug=slug)

@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    """ check if the order queryset exist before doing anything"""
    if order_qs.exists():
        order = order_qs[0]
        """check if the order item is in the order"""
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item,
                                                  user=request.user,
                                                  ordered=False)[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
                order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect('core:order_summary')
        else:
            messages.info(request, "This item was not in your cart")
            return redirect('core:product', slug=slug)
    else:
        # message the user doesnt have an other
        messages.info(request, "You do not have an active order")
        return redirect('core:product', slug=slug)







