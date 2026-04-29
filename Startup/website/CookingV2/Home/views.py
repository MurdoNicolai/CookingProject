from django.shortcuts import render

def home(request):
    return render(request, 'main/home.html')

def tailwind_test(request):
    return render(request, 'main/tailwind_test.html')
