import django_filters.rest_framework
from django.conf import settings
from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView
from rest_framework import generics, status
from rest_framework.response import Response
import operator

from .models import Question, QuestionOption, Voting
from .serializers import SimpleVotingSerializer, VotingSerializer
from base.perms import UserIsStaff
from base.models import Auth

class VotingList(TemplateView):
    template_name = 'voting/listVoting.html'
    
    def showVoting(request):
        votaciones = Voting.objects.all()

        data={
            'votaciones': votaciones
        }

        return render(request, 'voting/listVoting.html', data)



class VotingView(generics.ListCreateAPIView):
    queryset = Voting.objects.all()
    serializer_class = VotingSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('id', )

    def get(self, request, *args, **kwargs):
        version = request.version
        if version not in settings.ALLOWED_VERSIONS:
            version = settings.DEFAULT_VERSION
        if version == 'v2':
            self.serializer_class = SimpleVotingSerializer

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.permission_classes = (UserIsStaff,)
        self.check_permissions(request)
        for data in ['name', 'desc', 'question', 'question_opt']:
            if not data in request.data:
                return Response({}, status=status.HTTP_400_BAD_REQUEST)

        question = Question(desc=request.data.get('question'))
        question.save()
        for idx, q_opt in enumerate(request.data.get('question_opt')):
            opt = QuestionOption(question=question, option=q_opt, number=idx)
            opt.save()
        voting = Voting(name=request.data.get('name'), desc=request.data.get('desc'),
                question=question)
        voting.save()

        auth, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        auth.save()
        voting.auths.add(auth)
        return Response({}, status=status.HTTP_201_CREATED)


class VotingUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Voting.objects.all()
    serializer_class = VotingSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    permission_classes = (UserIsStaff,)

    def put(self, request, voting_id, *args, **kwars):
        action = request.data.get('action')
        if not action:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        voting = get_object_or_404(Voting, pk=voting_id)
        msg = ''
        st = status.HTTP_200_OK
        if action == 'start':
            if voting.start_date:
                msg = 'Voting already started'
                st = status.HTTP_400_BAD_REQUEST
            else:
                voting.start_date = timezone.now()
                voting.save()
                msg = 'Voting started'
        elif action == 'stop':
            if not voting.start_date:
                msg = 'Voting is not started'
                st = status.HTTP_400_BAD_REQUEST
            elif voting.end_date:
                msg = 'Voting already stopped'
                st = status.HTTP_400_BAD_REQUEST
            else:
                voting.end_date = timezone.now()
                voting.save()
                msg = 'Voting stopped'
        elif action == 'tally':
            if not voting.start_date:
                msg = 'Voting is not started'
                st = status.HTTP_400_BAD_REQUEST
            elif not voting.end_date:
                msg = 'Voting is not stopped'
                st = status.HTTP_400_BAD_REQUEST
            elif voting.tally:
                msg = 'Voting already tallied'
                st = status.HTTP_400_BAD_REQUEST
            else:
                voting.tally_votes(request.auth.key)
                msg = 'Voting tallied'
        else:
            msg = 'Action not found, try with start, stop or tally'
            st = status.HTTP_400_BAD_REQUEST
        return Response(msg, status=st)

def sortByName(request):
    voting = Voting.objects.all()
    dic = {}
    for v in voting:
        name = v.name
        dic[v] = name
    
    sd = dict(sorted(dic.items(), key=operator.itemgetter(1)))
    return render(request, 'voting/votingsByName.html', {'votacionesPorNombre':sd.keys})

def sortByDesc(request):
    voting = Voting.objects.all()
    dic = {}
    for v in voting:
        desc = v.desc
        dic[v] = desc
    
    sd = dict(sorted(dic.items(), key=operator.itemgetter(1)))
    return render(request, 'voting/votingsByDesc.html', {'votacionesPorDesc':sd.keys})

def sortByStartDate(request):
    voting = Voting.objects.all()
    dic = {}
    for v in voting:
        start_date = v.start_date
        if start_date!=None:
            dic[v] = start_date
    
    sd = dict(sorted(dic.items(), key=operator.itemgetter(1)))
    return render(request, 'voting/votingsByStartDate.html', {'votacionesPorStartDate':sd.keys})

def sortByEndDate(request):
    voting = Voting.objects.all()
    dic = {}
    for v in voting:
        end_date = v.end_date
        if end_date!=None:
            dic[v] = end_date
    
    sd = dict(sorted(dic.items(), key=operator.itemgetter(1)))
    return render(request, 'voting/votingsByEndDate.html', {'votacionesPorEndDate':sd.keys})
