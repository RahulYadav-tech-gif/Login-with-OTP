from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth.models import User
import random
import http.client
from django.conf import settings
from django.contrib.auth import authenticate, login
from twilio.rest import Client
from django.conf import settings

# Create your views here.

# def send_otp(mobile , otp):
#     print("FUNCTION CALLED")
#     conn = http.client.HTTPSConnection("api.msg91.com")
#     authkey = settings.AUTH_KEY 
#     headers = { 'content-type': "application/json" }
#     url = "http://control.msg91.com/api/sendotp.php?otp="+otp+"&message="+"Your_otp_is__"+otp +"&mobile="+mobile+"&authkey="+authkey+"&country=91"
#     conn.request("GET", url , headers=headers)
#     res = conn.getresponse()
#     data = res.read()
#     print(data)
#     return None

def send_otp(mobile, otp):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    message = client.messages.create(
        body=f"Your OTP is {otp}",
        from_=settings.TWILIO_PHONE_NUMBER,
        to=f"+91{mobile}"  
    )
    return message


def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')

        check_user = User.objects.filter(email = email).first()
        check_profile = Profile.objects.filter(mobile = mobile).first()


        if check_user or check_profile:
            context = {'message':'User already exists', 'class':'danger'}
            return render(request, 'register.html', context)

        username = email.split('@')[0] + str(random.randint(1000, 9999))
        user = User(username=username, email=email, first_name=name)
        user.save()        
        otp = str(random.randint(1000,9999))
        profile = Profile(user = user , mobile=mobile , otp = otp) 
        profile.save()
        send_otp(mobile, otp)
        request.session['mobile'] = mobile
        return redirect('otp')
    return render(request, 'register.html')
    


def login_attempt(request):
    if request.method == "POST":
        mobile = request.POST.get('mobile')

        user = Profile.objects.filter(mobile = mobile).first()

        if user is None:
            context = {'message':'User does not exists', 'class':'danger'}
            return render(request, 'login.html', context)

        otp = str(random.randint(1000, 9999))
        user.otp = otp
        user.save()
        send_otp(mobile, otp)
        request.session['mobile'] = mobile
        return redirect('login_otp')

    return render(request, 'login.html')

def login_otp(request):
    mobile = request.session.get('mobile')
    context = {'mobile':mobile}
    if request.method == "POST":
        otp = request.POST.get('otp')
        profile = Profile.objects.get(mobile=mobile)

        if otp == profile.otp:
            user = User.objects.get(id=profile.user.id)
            login(request, user)
            return redirect('welcome_page')
        else:
            print('Wrong')
            context = {'message':'Wrong OTP', 'class':'danger', 'mobile':mobile}
            return render(request, 'login_otp.html', context)

    return render(request, 'login_otp.html', context)
        


def otp(request):
    mobile = request.session['mobile']
    context = {'mobile': mobile}
    if request.method == 'POST':
        otp = request.POST.get('otp')
        profile = Profile.objects.filter(mobile=mobile).first()

        if otp == profile.otp:
            return redirect('welcome_page')
        else:
            print('Wrong')
            context = {'message':'Wrong OTP', 'class':'danger', 'mobile':mobile}
            return render(request, 'otp.html', context)

    return render(request, 'otp.html', context)
    

def welcome_page(request):
    return render(request, 'welcome_page.html')