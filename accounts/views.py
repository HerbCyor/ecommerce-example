from django.shortcuts import get_object_or_404, render, redirect
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
from django.contrib.auth.forms import SetPasswordForm, PasswordChangeForm
from django.db.models.query_utils import Q
from django.contrib.auth import update_session_auth_hash

from carts.views import _getCartIdbySession
from carts.models import Cart
from orders.models import OrderItem
from orders.models import Order
from .forms import RegistrationForm, ShippingAddressForm, UserForm, UserProfileForm
from .models import Account, ShippingAddress, UserProfile
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
        next_url = request.POST.get('next')
        
        if user is not None:

            try:
                cart = Cart.objects.get(cart_id=_getCartIdbySession(request))
                
                if cart:
                    cart.user = user
                    cart.save()
            except:
                pass

            auth.login(request, user)
            messages.success(request, "logged in")
            
            if next_url: #redirects to the original page if login request didn't come from the login link.
                return redirect(next_url)
            else:
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
    
    uid = request.session.get('uid') #used for password reset request from 'forgot password'

    try:
        user = Account.objects.get(pk=uid) #used for password reset request from 'forgot password'
        origin = 'forgot-password'
    except (Account.DoesNotExist):
        if request.user.is_authenticated:
            user = Account.objects.get(id=request.user.id) #password reset from dashboard
            origin = 'dashboard'
        else:
            return redirect('home')
    
    if request.method == 'POST': #password validation
        if origin == 'forgot-password':
            form = SetPasswordForm(user, request.POST)
        elif origin == 'dashboard':
            form = PasswordChangeForm(user, request.POST)
        
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "password successfully reset")
            return redirect('login')
        else:
            messages.error(request, "Errors:")
    else:
        if origin == 'forgot-password':
            form = SetPasswordForm(user)
        elif origin == 'dashboard':
            form = PasswordChangeForm(user)

    return render(request, "accounts/resetpassword.html", {'form':form, 'origin':origin})


@login_required(login_url='login')
def dashboard(request):

    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    profile = UserProfile.objects.get(user_id=request.user.id)
    context = {
        'orders': orders,
        'profile': profile,
    }
    return render(request, 'accounts/dashboard.html', context)

def my_orders(request):
    
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)

    context ={
        'orders':orders
    }
    return render(request, "accounts/my_orders.html", context)

def edit_profile(request):
    
    user = request.user
    profile = get_object_or_404(UserProfile, user=user)
    
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'profile updated')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=profile)

    # profile = UserProfile.objects.get(user=user)
    address_list = ShippingAddress.objects.filter(user=user)
    try:

        primary_address = ShippingAddress.objects.get(user_id=user.id, is_selected=True)
    except (ShippingAddress.DoesNotExist):
        primary_address = None
    shipping_address_form = ShippingAddressForm(request.POST)

    context = {
        'profile':profile,
        'address_list':address_list,
        'primary_address':primary_address,
        'shipping_address_form': shipping_address_form,
        'user_form':user_form,
        'profile_form':profile_form,
    }
    return render(request, "accounts/edit_profile.html", context)
@login_required(login_url='login')
def order_detail(request, order_number):

    order = Order.objects.get(order_number=order_number)
    order_items = OrderItem.objects.filter(order=order)

    context={
        'order':order,
        'order_items': order_items,
        'shipping_address': order.shipping_address,
        'payment':order.payment,
    }
    return render(request, 'accounts/order_detail.html', context)