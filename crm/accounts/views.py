from django.shortcuts import render, redirect
# from django.http import HttpResponse, JsonResponse
from .models import *
from .forms import OrderForm, CreateUserForm, CustomerForm  # for register
from django.forms import inlineformset_factory
from .filter import OrderFilter
from django.contrib.auth.forms import UserCreationForm  # for register
from django.contrib import messages  # flash message
from django.contrib.auth import authenticate, login, logout  # for login
from django.contrib.auth.decorators import login_required  # for login
from .decorators import unauthenticated_user, allowed_user, admin_only  # custom permission role name
from django.contrib.auth.models import Group

# Create your views here.



@login_required(login_url='login')  # check user login if not redirect to login page
@admin_only # check user with role name redirect to another page.
def home(request):
    customers = Customer.objects.all()
    orders = Order.objects.all()
    total_customers = customers.count()
    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()

    context = {
        'customers': customers,
        'orders': orders,
        'total_customers': total_customers,
        'total_orders': total_orders,
        'delivered': delivered,
        'pending': pending,
    }

    return render(request, 'accounts/dashboard.html', context)

@login_required(login_url='login')  # check user login if not redirect to login page
@allowed_user(allowed_roles=['customer'])  # allow only user role admin
def accountSettings(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)

    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
    context = {
        'form': form
    }
    return render(request, 'accounts/accounting_settings.html', context)


@login_required(login_url='login')  # check user login if not redirect to login page
@allowed_user(allowed_roles=['admin'])  # allow only user role admin
def products(request):
    data = Products.objects.all()
    return render(request, 'accounts/products.html', {'products': data})


@login_required(login_url='login')  # check user login if not redirect to login page
def customer(request, pk):
    customers = Customer.objects.get(id=pk)
    orders = customers.order_set.all()
    orders_count = orders.count()

    myFilter = OrderFilter(request.GET, queryset=orders)

    orders = myFilter.qs

    context = {
        'myFilter': myFilter,
        'customers': customers,
        'orders': orders,
        'orders_count': orders_count,
    }

    return render(request, 'accounts/customer.html', context)


# def createOrder(request):
#     form = OrderForm()
#     if request.method == 'POST':
#         form = OrderForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('/')
#     context = {
#         'form': form
#     }
#     return render(request, 'accounts/order_form.html', context)
@login_required(login_url='login')  # check user login if not redirect to login page
def createOrder(request, pk):
    OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'), extra=10)
    customer = Customer.objects.get(id=pk)
    # form = OrderForm(instance={'customer': customer})
    formset = OrderFormSet(queryset=Order.objects.none(), isinstance=customer)
    if request.method == 'POST':
        formset = OrderFormSet(request.POST, isinstance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')
    context = {
        'formset': formset
    }
    return render(request, 'accounts/order_form.html', context)


@login_required(login_url='login')  # check user login if not redirect to login page
def updateOrder(request, pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')
    context = {
        'form': form,
    }
    return render(request, 'accounts/order_form.html', context)


@login_required(login_url='login')  # check user login if not redirect to login page
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('/')
    context = {
        'item': order
    }

    return render(request, 'accounts/delete.html', context)


@unauthenticated_user  # if user was loggined true so cannot access to this function
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, f'Wrong Username or password!')
    context = {

    }
    return render(request, 'accounts/login.html', context)


@login_required(login_url='login')  # check user login if not redirect to login page
def logoutUser(reqeust):
    logout(reqeust)
    return redirect('login')


@unauthenticated_user  # if user was loggined true so cannot access to this function
def registerPage(request):
    # check user is online logined
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            # save user register to group role 'customer'
            user = form.save()
            group = Group.objects.get(name='customer')
            user.groups.add(group)
            # save user register make relationship with table customer
            Customer.objects.create(user=user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account was created for {username}')
            return redirect('login')
    context = {
        'form': form
    }
    return render(request, 'accounts/register.html', context)

@login_required(login_url='login')
@allowed_user(allowed_roles=['customer'])
def userPage(request):
    orders = request.user.customer.order_set.all()
    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()

    context = {
        'orders': orders,
        'total_orders': total_orders,
        'delivered': delivered,
        'pending': pending,
    }
    return render(request, 'accounts/user.html', context)
