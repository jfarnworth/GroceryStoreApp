from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
import ast
from datetime import datetime
from .forms import SignInForm

from .models import Customers, Products, Reservations


def sign_in(request):
    form_class = SignInForm

    name = request.POST.get('cust_name')
    id = request.POST.get('cust_id')

    if name:
        if request.POST.get('new_customer'):
            # check db for name
            try:
                if Customers.objects.get(name=name):
                    msg = 'Customer name already exists. Try another?'

            except ObjectDoesNotExist:
                # create new entry in db
                temp_id = Customers.objects.latest('id').id
                temp_id += 1
                Customers.objects.create(id=temp_id, name=name)
                # redirect to reservations page
                return redirect('/reservations/{}/{}'.format(name, temp_id))
        else:
            try:
                if id:
                    Customers.objects.get(name=name, id=id)
                    # GREAT! THEY PASS!
                    return redirect('/reservations/{}/{}'.format(name, id))
                else:
                    msg = 'Do you know your ID? I need that as well.'
            except ObjectDoesNotExist:
                msg = 'That didn\'t work, try again.'

        return render(request, 'smiths_app/index.html', {'form': form_class, 'msg': msg})

    else:
        return render(request, 'smiths_app/index.html', {'form': form_class})


def reservations(request, user_name, user_id, reservation_id=None):
    products = Products.objects.all()
    reservation = None
    reserved_dict = None
    msg = ''

    if request.POST.get('logOut'):
        return redirect('/index')

    elif request.POST.get('saveRes'):  # new reservation
        id = Reservations.objects.latest('id').id
        id += 1
        date = datetime.strftime(datetime.now().date(), '%m/%d/%y')
        barcode_list = []
        quantity_list = []

        # get all form values
        for key in request.POST:
            broken = key.split('-')
            try:
                if ('amount' in broken or 'quantity' in broken) and request.POST.get(key):
                    if 'amount' in broken:
                        quantity_list.append(request.POST.get(key))
                    else:
                        quantity_list.append(request.POST.get(key))
                    barcode_list.append(int(broken[0]))
            except IndexError:
                pass

        barcode_list = barcode_list
        quantity_list = quantity_list

        # save to reservations in db
        Reservations.objects.create(id=id, r_date=date, quantities=quantity_list, customer_id=user_id, barcodes=barcode_list)

        reservation_id = id
        msg = "Reservation successfully created!"

    elif request.POST.get('updateRes'):
        reservation_id = request.POST.get('reservation_id')
        date = datetime.strftime(datetime.now().date(), '%m/%d/%y')
        barcode_list = []
        quantity_list = []

        # get all form values
        for key in request.POST:
            broken = key.split('-')
            try:
                if ('amount' in broken or 'quantity' in broken) and request.POST.get(key):
                    if 'amount' in broken:
                        quantity_list.append(request.POST.get(key))
                    else:
                        quantity_list.append(request.POST.get(key))
                    barcode_list.append(int(broken[0]))
            except IndexError:
                pass

        barcode_list = barcode_list
        quantity_list = quantity_list

        # save to reservations in db
        Reservations.objects.filter(id=reservation_id, customer_id=user_id).update(r_date=date, quantities=quantity_list, barcodes=barcode_list)

        msg = "Reservation successfully updated!"

    elif request.POST.get('newRes'):  # new reservation -> bypass reservation and load view
        reservation_id = None

    elif request.POST.get('deleteRes'):  # bypass reservation and load view
        if request.POST.get('delete_id'):
            reservation_id = request.POST.get('delete_id')
            Reservations.objects.filter(id=reservation_id).delete()
            msg = 'Reservation successfully deleted'
        else:
            msg = 'No reservation to delete'

        reservation_id = None

    elif request.POST.get('loadRes'):
        reservation_id = request.POST.get('loadReservation')

    if reservation_id:
        try:
            reservation = Reservations.objects.get(id=reservation_id)
            if reservation.customer_id == int(user_id):
                # dict of barcodes and quantities
                reserved_dict = {}
                barcodes = ast.literal_eval(reservation.barcodes)
                quantities = ast.literal_eval(reservation.quantities)

                i = 0
                for each in barcodes:
                    reserved_dict[each] = quantities[i]
                    i += 1

            else:
                reservation = None
                reserved_dict = None
                msg = 'Mismatch: Invalid reservation ID'

        except ObjectDoesNotExist:
            msg = 'Missing: Invalid reservation ID'

    return render(request, 'smiths_app/reservation_selection.html', {'products': products, 'reservation': reservation,
                                                                     'reserved_dict': reserved_dict, 'user_name': user_name,
                                                                     'user_id': user_id, 'msg': msg})
