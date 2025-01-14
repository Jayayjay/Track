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




# Create your views here.
# def record_view(request):
#     athlete_records = AthleteRecords.objects.all()
#     context = {'athlete_records': athlete_records}
#     return render(request, 'templates/records/record.html')
#     return render(request, 'record/records.html')

# def new_record_view(request):
#     if request.method == "POST":
#         form = AthleteRecordsForms(request.POST)
#         if form.is_valid():
#             form.save()
    
#     return redirect('')