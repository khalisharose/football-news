from django.shortcuts import render

def show_main(request):
    context = {
        'npm' : '2406496183',
        'name': 'Khalisha Roselani',
        'class': 'PBP F'
    }

    return render(request, "main.html", context)

# Create your views here.
