from django.shortcuts import render, get_list_or_404
from django.http import HttpResponse
from datetime import date
from .models import Meet, Event

# Create your views here.
def index(request):
    current_meets = Meet.objects.filter(startDate__lte=date.today()).filter(endDate__gte=date.today())
    upcoming_meets = Meet.objects.filter(startDate__gt=date.today())
    context = {'current_meets': current_meets, 'upcoming_meets': upcoming_meets}
    return render(request, 'core/index.html', context)