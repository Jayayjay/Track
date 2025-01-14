from django.shortcuts import render, redirect
from .models import AthleteRecords
from .forms import AthleteRecordsForms
from rest_framework.permissions import (
    IsAuthenticated,
)
from rest_framework.views import APIView
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
)
from rest_framework.response import Response
from .serializers import AthleteSerializer
from .forms import AthleteRecordsForms
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from .models import AthleteRecords
from .serializers import AthleteSerializer

class AthleteList(ListAPIView):
    allowed_methods = ['GET']
    serializer_class = AthleteSerializer
    queryset = AthleteRecords.objects.all()

    def get(self, request, *args, **kwargs):
        # Get all athlete records from the database
        athlete_records = self.get_queryset()
        
        # If the request is from a browser, render the HTML template
        if request.META.get('HTTP_ACCEPT', '').startswith('text/html'):
            return render(request, 'records/record_detail.html', {'athlete_records': athlete_records})
        
        # Otherwise, return JSON as usual
        return super().get(request, *args, **kwargs)


class CreateAthlete(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AthleteSerializer

    def post(self, request, *args, **kwargs):
        # If the request is from an API, process normally
        if request.META.get('HTTP_ACCEPT', '').startswith('application/json'):
            return super().post(request, *args, **kwargs)
        
        # If the request is from a browser, process the form submission
        form = AthleteRecordsForms(request.POST)
        if form.is_valid():
            form.save()
            return redirect('record_view')  # Redirect to the records page
        return render(request, 'records/new_record.html', {'form': form})

    def get(self, request, *args, **kwargs):
        # Render the HTML form for creating a new athlete
        form = AthleteRecordsForms()
        return render(request, 'records/new_record.html', {'form': form})



# Create your views here.
def record_view(request):
    athlete_records = AthleteRecords.objects.all()
    context = {'athlete_records': athlete_records}
    return render(request, 'records/new_record.html')
    
def new_record_view(request):
    if request.method == "POST":
        form = AthleteRecordsForms(request.POST)
        if form.is_valid():
            form.save()
    
    return redirect('')