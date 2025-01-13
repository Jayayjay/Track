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

class AthleteList(ListAPIView):
    allowed_methods = ['GET']
    serializer_class = AthleteSerializer
    queryset = AthleteRecords.objects.all()


class CreateAthlete(CreateAPIView):
    permission_classes = [IsAuthenticated,]
    serializer_class = AthleteSerializer


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