from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from userauths import forms as userauths_forms
from vendor import models as vendor_models
from userauths import models as userauths_models

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
        login(request, user)

        messages.success(request, f"Account creation for {full_name} is successful")
        profile = userauths_models.Profile.objects.create(user=user, full_name=full_name, mobile=mobile)

        if user_type == "Vendor":
            vendor_models.Vendor.objects.create(user=user, store_name=full_name)
            profile.user_Type = "Vendor"
        else:
            profile.user_Type = "Customer"
        profile.save()

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
