from django.shortcuts import render
from cars_project.forms import CarForm, LoginForm, RegisterForm


def home_view(request):
  return render(request, "home.html")
def upload_image_view(request):
  form = CarForm()
  return render(request, "upload_image.html", {'form': form})
def login_view(request):
  form = LoginForm()
  return render(request, "login.html", {'form': form})
def register_view(request):
  form = RegisterForm()
  return render(request, "register.html", {'form': form})