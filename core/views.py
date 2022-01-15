from django.shortcuts import get_object_or_404, render, get_list_or_404
from django.http import HttpResponse
from datetime import date
from .models import Meet, Event

# Create your views here.
def overview(request):
    current_meets = Meet.objects.filter(startDate__lte=date.today()).filter(endDate__gte=date.today())
    upcoming_meets = Meet.objects.filter(startDate__gt=date.today())
    context = {'current_meets': current_meets, 'upcoming_meets': upcoming_meets}
    return render(request, 'core/overview.html', context)

def detail(request, meet_id):
    meet = get_object_or_404(Meet, pk=meet_id)
    return render(request, 'core/detail.html', {'meet': meet})

def entries(request, meet_id, event_id):
    event = get_object_or_404(Event, pk=event_id)
    return render(request, 'core/entries.html', {'event': event})