from django.shortcuts import render
from django.http import HttpResponse
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_text

from user.models import CustomUser
from .verification_tokens import account_activation_token


def activate(request, uidb64, token):
	try:
		uid = force_text(urlsafe_base64_decode(uidb64))
		user = CustomUser.objects.get(pk = uid)
	except(TypeError, ValueError, OverflowError):
		user = None
	if user is not None and account_activation_token.check_token(user, token):
		user.is_active = True
		user.save()
		# login(request, user)
		return HttpResponse("Thank you, your email has been confirmed!")

	else:
		return HttpResponse("Invalid Activation Link. Try resending activation link.")