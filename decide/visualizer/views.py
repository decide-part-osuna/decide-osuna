import json
from django.views.generic import TemplateView
from django.conf import settings
from django.http import Http404

from base import mods

from django.shortcuts import render, get_object_or_404, HttpResponse, redirect
from django.template.loader import get_template
from visualizer.models import Mail

def listaCorreos(request, voting_id):
        if request.method == 'POST':
            email = request.POST["email"]
            listaCorreos = Mail(mail=email,voting_id=voting_id)
            if not Mail.objects.filter(mail=email, voting_id=voting_id).exists():
                listaCorreos.save()
            return redirect('Visualizer', str(voting_id))
        
        

class VisualizerView(TemplateView):
    template_name = 'visualizer/visualizer.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vid = kwargs.get('voting_id', 0)

        try:
            r = mods.get('voting', params={'id': vid})
            context['voting'] = json.dumps(r[0])
        except:
            raise Http404

        return context       
