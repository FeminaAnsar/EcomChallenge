from django.shortcuts import render,redirect,HttpResponseRedirect
from .models import Customer,Products,Order,Category
from django.views import View
from django.contrib.auth.hashers import check_password,make_password
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
import datetime

class Index(View):
    def post(self,request):
        product=request.POST.get('product')
        remove=request.POST.get('remove')
        cart=request.session.get('cart')
        if cart:
            quantity=cart.get(product)
            if quantity:
                if remove:
                    if quantity<=1:
                        cart.pop(product)
                    else:
                        cart[product]=quantity-1
                else:
                    cart[product]=quantity+1
            else:
                cart[product]=1
        else:
            cart={}
            cart[product]=1
        request.session['cart']=cart
        print('cart',request.session['cart'])
        return redirect('home')
    def get(self,request):
        return HttpResponseRedirect(f'/{request.get_full_path()[1:]}')

def ecomapp(request):
    cart = request.session.get('cart')
    if not cart:
        request.session['cart'] = {}
    products = None
    categories = Category.get_all_categories()
    categoryID = request.GET.get('category')
    if categoryID:
        products = Products.get_all_products_by_categoryid(categoryID)
    else:
        products = Products.get_all_products()

    data = {}
    data['products'] = products
    data['categories'] = categories

    messages.success(request,'you are : ', request.session.get('email'))
    return render(request, 'index.html', data)

class Login(View):
    return_url=None

    def get(self,request):
        Login.return_url=request.GET.get('return_url')
        return render(request,'login.html')

    def post(self,request):
        email=request.POST.get('email')
        password=request.POST.get('password')
        customer=Customer.get_customer_by_email(email)
        error_message=None
        if customer:
            flag=check_password(password,customer.password)
            if flag:
                request.session['customer']=customer.id
                if Login.return_url:
                    return HttpResponseRedirect(Login.return_url)
                else:
                    Login.return_url=None
                    return redirect('home')
            else:
                error_message='Invalid!!!'
        else:
            error_message = 'Invalid!!!'
        messages.success(request,email,password)
        return render(request,'login.html',{'error':error_message})

def Logout(request):
    request.session.clear()
    return redirect('login')

class Signup(View):
    def get(self,request):
        return render(request,'signup.html')

    def post(self,request):
        postData=request.POST
        first_name=postData.get('firstname')
        last_name=postData.get('lastname')
        phone=postData.get('phone')
        email=postData.get('email')
        password=postData.get('password')
        value={'first_name':first_name,
                'last_name' :last_name,
               'phone':phone,
               'email':email
                }
        error_message=None
        customer=Customer(first_name=first_name,
                          last_name=last_name,
                          phone=phone,
                          email=email,
                          password=password)
        error_message=self.validateCustomer(customer)
        if not error_message:
            print(first_name,last_name,phone,email,password)
            customer.password=make_password(customer.password)
            customer.register()
            return redirect('home')
        else:
            data={'error': error_message,
                  'values':value
                  }
            return render(request,'signup.html',data)

    def validateCustomer(self,customer):
        error_message=None
        if(not customer.first_name):
            error_message="Please enter your first name!"

        if (not customer.last_name):
            error_message = "Please enter your lasst name!"

        if (not customer.phone):
            error_message = "Please enter your Mobile number!"

        if(not customer.email):
            error_message="Please enter your Email"
        return error_message

@method_decorator(login_required, name='post')
class CheckOut(View):
    def post(self,request):
        address=request.POST.get('address')
        phone=request.POST.get('phone')
        customer=request.session.get('customer')
        cart=request.session.get('cart')
        products=Products.get_product_by_id(list(cart.keys()))
        print(address,phone,customer,cart,products)

        for product in products:
            print(cart.get(str(product.id)))
            order=Order(customer=Customer(id=customer),
                        product=product,
                        price=product.price,
                        address=address,
                        phone=phone,
                        quantity=cart.get(str(product.id)))

            order.save()

        request.session['cart']={}
        return redirect('cart')

@method_decorator(login_required, name='get')
class OrderView(View):
    def get(self,request):
        customer=request.session.get('customer')
        orders=Order.get_orders_by_customer(customer)
        print(orders)
        return render(request,'orders.html',{'orders':orders})

@method_decorator(login_required, name='get')
class Cart(View):
    def get(self,request):
        ids=list(request.session.get('cart').keys())
        products=Products.get_product_by_id(ids)
        print(products)
        return render(request,'cart.html',{'products':products})



# Create your views here.
