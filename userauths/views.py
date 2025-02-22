from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from userauths import forms as userauths_forms
from vendor import models as vendor_models
from userauths import models as userauths_models

from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib import messages
from django.urls import reverse

User = get_user_model()

# Password Reset Request View
def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "No user found with this email address.")
            return redirect("password_reset_request")

        # Generate password reset token and URL
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = request.build_absolute_uri(
            reverse("userauths:password_reset_confirm", kwargs={"uidb64": uid, "token": token})
        )

        # Prepare email content
        subject = "Password Reset Request"
        text_body = render_to_string("password_reset_email.txt", {
            "user": user,
            "reset_url": reset_url,
        })
        html_body = render_to_string("password_reset_email.html", {
            "user": user,
            "reset_url": reset_url,
        })

        # Send email
        msg = EmailMultiAlternatives(
            subject=subject,
            from_email=settings.FROM_EMAIL,
            to=[user.email],
            body=text_body,
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send()

        messages.success(request, "Password reset email has been sent. Please check your inbox.")
        return redirect("userauths:password_reset_done")

    return render(request, "password_reset.html")

# Password Reset Done View
def password_reset_done(request):
    return render(request, "password_reset_done.html")

# Password Reset Confirm View
def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            new_password = request.POST.get("new_password")
            user.set_password(new_password)
            user.save()
            messages.success(request, "Your password has been reset successfully. You can now log in.")
            return redirect("userauths:password_reset_complete")

        return render(request, "password_reset_confirm.html")
    else:
        messages.error(request, "Invalid password reset link. Please try again.")
        return redirect("userauths:password_reset_request")

# Password Reset Complete View
def password_reset_complete(request):
    return render(request, "password_reset_complete.html")

# def register_view(request):
#     if request.user.is_authenticated:
#         messages.warning(request, "You are already logged in")
#         return redirect("/")

#     form = userauths_forms.UserRegisterForm(request.POST or None)
#     if form.is_valid():
#         user = form.save()
#         full_name = form.cleaned_data.get("full_name")
#         email = form.cleaned_data.get("email")
#         password = form.cleaned_data.get("password1")
#         mobile = form.cleaned_data.get("mobile")
#         user_type = form.cleaned_data.get("user_type")

#         user = authenticate(email=email, password=password)
#         login(request, user)

#         messages.success(request, f"Account creation for {full_name} is successful")
#         profile = userauths_models.Profile.objects.create(user=user, full_name=full_name, mobile=mobile)

#         if user_type == "Vendor":
#             vendor_models.Vendor.objects.create(user=user, store_name=full_name)
#             profile.user_Type = "Vendor"
#         else:
#             profile.user_Type = "Customer"
#         profile.save()

#         next_url = request.GET.get("next", "store:index")
#         return redirect(next_url)

#     context = {"form": form}
#     return render(request, 'sign-up.html', context)

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from anymail.exceptions import AnymailError

def register_view(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in")
        return redirect("/")

    form = userauths_forms.UserRegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        full_name = form.cleaned_data.get("full_name")
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password1")
        mobile = form.cleaned_data.get("mobile")
        user_type = form.cleaned_data.get("user_type")

        user = authenticate(email=email, password=password)
        

        messages.success(request, f"Account creation for {full_name} is successful")
        profile = userauths_models.Profile.objects.create(user=user, full_name=full_name, mobile=mobile)
        
        if user_type == "Vendor":
            vendor_models.Vendor.objects.create(user=user, store_name=full_name)
            profile.user_Type = "Vendor"
        else:
            profile.user_Type = "Customer"
        profile.save()

        # Send a welcome email to the new user
        subject = "Welcome to Our Site"
        text_body = render_to_string("welcome_email.txt", {"user": user})
        html_body = render_to_string("welcome_email.html", {"user": user})

        try:
            # Attempt to send the email using Anymail
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_body,
                from_email=settings.FROM_EMAIL,
                to=[email],
            )
            msg.attach_alternative(html_body, "text/html")
            msg.send()

        except AnymailError as e:
            # Handle Mailgun errors (e.g., unauthorized recipient)
            error_message = str(e)
         
                # Notify yourself about the unauthorized email
            admin_subject = "Unauthorized Email Registration Attempt"
            admin_text_body = render_to_string("unauthorized_email.txt", {"email": email})
            admin_html_body = render_to_string("unauthorized_email.html", {"email": email})
            
            admin_msg = EmailMultiAlternatives(
                subject=admin_subject,
                body=admin_text_body,
                from_email=settings.FROM_EMAIL,
                to=[settings.ADMIN_EMAIL],
            )
            admin_msg.attach_alternative(admin_html_body, "text/html")
            admin_msg.send()
            
            messages.warning(request, "Your email is not authorized. An email has been sent to the admin for approval.")
            return redirect("userauths:sign-in")

        login(request, user)
        next_url = request.GET.get("next", "store:index")
        return redirect(next_url)

    context = {"form": form}
    return render(request, 'sign-up.html', context)

def login_view(request):
	if request.user.is_authenticated:
		messages.warning(request,"You are already logged in")
		return redirect("/")
	if request.method=="POST":
		form=userauths_forms.LoginForm(request.POST or None)
		if form.is_valid():
			email = form.cleaned_data['email']
			password=form.cleaned_data['password']
			captcha_verified=form.cleaned_data.get("captcha",False)
			if captcha_verified:
				try:
					user_instance = userauths_models.User.objects.get(email=email, is_active=True)
					user_authenticate = authenticate(request,email=email,password=password)
					if user_instance is not None:
						login(request,user_authenticate)
						messages.success(request,"You are logged in")
						next_url=request.GET.get("next","store:index")
						return redirect(next_url)
					else:
						messages.error(request,"Username or password does not exist")
				except:
					messages.error(request,"user does not exist")
			else:
				messages.error(request,"Captcha verification failed please try again")
	else:
		form=userauths_forms.LoginForm()
	context={
		"form":form
	}
	return render(request,"sign-in.html",context)

def logout_view(request):
	if 'card_id' in request.session:
		card_id=request.session['card_id']
	else:
		card_id=None
  
	logout(request)
 
	request.session['card_id']=card_id
	messages.success(request,"You have been logged out")
	return redirect("userauths:sign-in")
