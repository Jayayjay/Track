from django.shortcuts import render, redirect
from athlete_records.models import AthleteRecords
from .forms import AthleteRecordsForms
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import AthleteSerializer

class AthleteList(APIView):
    def get(self, request):
        athlete_records = AthleteRecords.objects.all()
        serializer = AthleteSerializer(athlete_records, many=True)
        return Response(serializer.data)





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