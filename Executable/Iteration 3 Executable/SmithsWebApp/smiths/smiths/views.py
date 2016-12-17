from django.shortcuts import render

# import model

def home(request):
    return render(request, 'index.html')
