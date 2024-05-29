from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.models import User
from .models import Product
from django.contrib.auth import authenticate,login,logout
from django.db.models import Q
from .models import Cart
import random
import razorpay

from django.core.mail import send_mail

from .models import Order

# Create your views here.
def home(request):
    context={}
    p=Product.objects.filter(is_active=True)
    print(p)
    context['products']=p
    # userid=request.user.id  
    # print(userid)
    # print('Result is : ',request.user.is_authenticated)
    return render(request,'index.html',context)

def product_details(request,pid):  #pid=4
    p=Product.objects.filter(id=pid)
    # print(p)
    context={}
    context['products']=p
    return render(request,'product_details.html',context)

def register(request):
    if request.method=='POST':
        uname=request.POST['uname']
        upass=request.POST['upass']
        ucpass=request.POST['ucpass']
        context={}
        if uname=="" or upass=="" or ucpass=="":# F or F or F=>F
            context['errmsg']="Fields cannot be Empty"
        elif upass != ucpass: #dhanashree15 != dhanashree15=>F
            context['errmsg']="Password & confirm password didn't match"
        else:
            try:
                u=User.objects.create(password=upass,username=uname,email=uname)
                u.set_password(upass)
                u.save()
                context['success']="User Created Successfully, Please Login"
            except Exception:
                context['errmsg']="User with same username already exists!!!!"
        #return HttpResponse("User created successfully!!")
        return render(request,'register.html',context)
    else:
        return render(request,'register.html')

def user_login(request):
    if request.method=='POST':
        uname=request.POST['uname']
        upass=request.POST['upass']
        print(uname,'-',upass)
        context={}
        if uname=="" or upass=="":
            context['errmsg']="Fields cannot be Empty"
            return render(request,'login.html',context)
        else:
            u = authenticate(username=uname, password=upass)

            if u is not None:
                login(request,u)
                return redirect('/')
            else:
                context['errmsg']="Invalid username and password"
                return render(request,'login.html',context)
            
    else:
        return render(request,'login.html')
    

def user_logout(request):
    logout(request)
    return redirect('/')

def catfilter(request,cv):
    q1=Q(cat=cv)
    q2=Q(is_active=True)
    p=Product.objects.filter(q1 & q2)
    print(p)
    context={}
    context['products']=p
    return render(request,'index.html',context)

def sort(request,sv):
    if sv== '0':
        #ascending
        col= 'price'
    else:
        #descending
        col= '-price'

    p=Product.objects.order_by(col)
    context={}
    context['products']=p
    return render(request,'index.html',context)

def range(request):
    min=request.GET['min']
    max=request.GET['max']
    q1=Q(price__gte=min)
    q2=Q(price__lte=max)
    q3=Q(is_active=True)
    p=Product.objects.filter(q1&q2&q3)
    context={}
    context['products']=p
    return render(request,'index.html',context)

def addtocart(request,pid):
    if request.user.is_authenticated:
        userid=request.user.id
        u=User.objects.filter(id=userid)   #4th object
        p=Product.objects.filter(id=pid)   #1st object
        #check product exist or not
        q1=Q(uid=u[0])
        q2=Q(pid=p[0])
        c=Cart.objects.filter(q1 & q2)
        print(c)  # queryset[<object 3>] 
        n=len(c)   # 1
        context={}
        if n == 1: 
            context['msg']="Product Already Exist in cart!!"
        else:
            c=Cart.objects.create(uid=u[0],pid=p[0])
            c.save()
            context['success']="Product Added Successfully to Cart!!"
        context['products']=p
        return render(request,'product_details.html',context)
        # return HttpResponse("product added in cart")
    else:
        return redirect('/login')
    

def viewcart(request):
    c=Cart.objects.filter(uid=request.user.id)  #uid=2
    # print(c)  # queryset[<object1>, <object2>]
    np=len(c)    #2
    s=0
    for x in c:
        s=s + x.pid.price * x.qty
    print(s)
    context={}
    context['data']=c
    context['total']=s
    context['n']=np
    return render(request,'cart.html',context)

def remove(request,cid):   #cid=10
    c=Cart.objects.filter(id=cid)   #id=10
    c.delete()
    return redirect('/viewcart')

def updateqty(request,qv,cid):
    c=Cart.objects.filter(id=cid)
    if not c.exists():
        print("Cart not found")
        return redirect('/viewcart')
    
    print(c)
    print(c[0])
    print(c[0].qty)
    if qv=='1':
        t=c[0].qty + 1
        c.update(qty=t)
    else:
        if c[0].qty>1:
            t=c[0].qty - 1
            c.update(qty=t)
    return redirect('/viewcart')

def placeorder(request):
    userid=request.user.id
    c=Cart.objects.filter(uid=userid)
    print(c)
    oid=random.randrange(1000,9999)
    for x in c:
        # print(x)
        # print(x.pid,"=",x.uid,"-",x.qty)
        o=Order.objects.create(order_id=oid,pid=x.pid,uid=x.uid,qty=x.qty)
        o.save()
        x.delete()
    context={}
    orders=Order.objects.filter(uid=request.user.id)
    np=len(orders)
    context['data']=orders
    context['n']=np
    s=0
    for x in orders:
        s=s + x.pid.price * x.qty
    context['total']=s

    
    #return HttpResponse("In placeorder")
    return render(request,'place_order.html',context)

def oremove(request,cid):   #cid=10
    c=Order.objects.filter(id=cid)   #id=10
    c.delete()
    return redirect('/placeorder')

def makepayment(request):
    orders=Order.objects.filter(uid=request.user.id)
    s=0
    for x in orders:
        s=s + x.pid.price * x.qty
        oid=x.order_id
    client = razorpay.Client(auth=("rzp_test_GPve3NiWquFtfe", "VOa82sng1RzjS42HpkAg0raO"))

    data = { "amount": s*100, "currency": "INR", "receipt": "oid" }
    payment = client.order.create(data=data)
    context={}
    context['data']=payment
    uemail=request.user.email
    context['uemail']=uemail
    # return HttpResponse('In Makepayment')
    return render(request,'pay.html',context)

def sendusermail(request,uemail):
    send_mail(
    "Ekart - order placed successfully",
    "Order details are:------",
    "tanujachavan85@gmail.com",
    [uemail],
    fail_silently=False,
    )

    return render(request,'ack.html')

def acknow(request):
    return render(request,'ack.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')