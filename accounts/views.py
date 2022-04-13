from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib import messages

#account verification imports
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
#reset form
from django.contrib.auth.forms import SetPasswordForm
from django.db.models.query_utils import Q
from django.contrib.auth import update_session_auth_hash
# Create your views here.

def register(request):
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            username = email.split("@")[0]
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password1'] #password validation on forms.RegisterForm.clean

            user = Account.objects.create_user(
                first_name = first_name,
                last_name = last_name,
                username = username,
                email = email,
                password = password,
            )
            user.phone_number = phone_number
            user.save()

            #user activation code generation and email
            current_site = get_current_site(request) #gets domain
            mail_subject = "Herbs e-commerce account verification"
            message = render_to_string("accounts/account_verification_email.html", {
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.id)), #encodes uid
                'token':default_token_generator.make_token(user), #creates token
            })
            to_email = email
            send_email = EmailMessage(subject=mail_subject, body=message, to=[to_email])
            send_email.send()

            # messages.sucess(request, "User successfully registered")
            return render(request, "accounts/verification_notice.html")

    else:

        form = RegistrationForm()

    context = {
        'form': form
    }
    return render(request, 'accounts/register.html', context)


def login(request):
   
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)
        
        if user is not None:
            auth.login(request, user)
            messages.success(request, "logged in")
            return redirect('dashboard')
        else:
            messages.error(request, "Wrong username or password")
            return redirect('login')

    return render(request, 'accounts/login.html')


@login_required(login_url='login')
def logout(request):
    
    auth.logout(request)
    return redirect('home')

def activate(request, uidb64, token):
    
    try:
        uid = urlsafe_base64_decode(uidb64).decode() #decodes uid
        user = Account._default_manager.get(pk=uid)
    
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token): #checks token
        user.is_active = True
        user.save()
        return render(request, "accounts/successful_verification.html")
    
    else:
        return render(request, "accounts/failed_verification.html")


def password_reset_request(request):
    
    if request.method == "POST":
        email = request.POST['email']

        if Account.objects.filter(email=email).exists():

            user = Account.objects.get(email__exact=email) #gets user with __exact attribute
            
            #user password reset email generation
            current_site = get_current_site(request)
            mail_subject = "Herbs e-commerce password reset"
            message = render_to_string("accounts/reset_password_email.html", {
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.id)),
                'token':default_token_generator.make_token(user),
            })
            send_email = EmailMessage(subject=mail_subject,body=message,to=[email])
            send_email.send()

            messages.success(request, "Password reset email sent.")
            return redirect('password_reset_request')
        else:
            messages.error(request,'Account not found')
            return redirect('password_reset_request')

    return render(request, 'accounts/password_reset_request.html')

def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode() #decodes uid
        user = Account._default_manager.get(pk=uid)
    
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token): #check token
        request.session['uid'] = uid #saves decoded uid into session to be fetched on resetpassword()
        return redirect('resetpassword')
    else:
        messages.error(request, "Link expired")
        return redirect('login') #change

def resetpassword(request):
    uid = request.session.get('uid')
    user = Account.objects.get(pk=uid)
    
    
    if request.method == 'POST': #password validation
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "password successfully reset")
            return redirect('login')
        else:
            messages.error(request, "Errors:")
    else:
        form = SetPasswordForm(user)
        
    return render(request, "accounts/resetpassword.html", {'form':form})


@login_required(login_url='login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')