from django.shortcuts import render
from cars_project.forms import CarForm


def home_view(request):
  return render(request, "home.html")
def upload_image_view(request):
  form = CarForm()
  return render(request, "upload_image.html", {'form': form})