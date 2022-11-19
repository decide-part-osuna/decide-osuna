from django.shortcuts import render
import json
from django.views.generic import TemplateView

# def inicio(request):
#     return render(request,'base.html')

class IndexView(TemplateView):
    
    def inicio(request):
        return render(request,'index.html')