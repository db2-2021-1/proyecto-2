from django.shortcuts import render

def mainpage(request):
  return render(request,'index.html')

def dashboard(request):
  return render(request, 'dashboard.html')