from django.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import post_save
from django.dispatch import receiver

from base import mods
from base.models import Auth, Key

from django.shortcuts import render, get_object_or_404, HttpResponse, redirect
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages
from django.template.loader import get_template
from visualizer.models import Mail


class Question(models.Model):
    
    desc = models.TextField(default=" ")
    questionYesNO = models.BooleanField(default=False, help_text="¿Quieres una pregunta de sí o no?")
    
    def __str__(self):
        return self.desc
    
@receiver(post_save, sender=Question)
def questionYesNO(sender, instance, **kwargs):
    options = instance.options.all()
    if instance.questionYesNO==True and options.count()==0:
        op1 = QuestionOption(question=instance, number=1, option="Sí")
        op1.save()
        op2 = QuestionOption(question=instance, number=2, option="No")
        op2.save()


class QuestionOption(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    number = models.PositiveIntegerField(blank=True, null=True)
    option = models.TextField(blank=True)

    def save(self):
        if not self.number:
            self.number = self.question.options.count() + 2
        
        return super().save()

    def __str__(self):
        return '{} ({})'.format(self.option, self.number)


class Voting(models.Model):
    name = models.CharField(max_length=200)
    desc = models.TextField(blank=True, null=True)
    question = models.ManyToManyField(Question, related_name='voting')

    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    pub_key = models.OneToOneField(Key, related_name='voting', blank=True, null=True, on_delete=models.SET_NULL)
    auths = models.ManyToManyField(Auth, related_name='votings')

    tally = JSONField(blank=True, null=True)
    postproc = JSONField(blank=True, null=True)


    def enviar_correo(self):
        for mailList in Mail.objects.filter(voting_id=self.id):
            correo = mailList.mail
            voting=Voting.objects.get(id=self.id)
            mensaje = 'Ya están los resultados de la votación: '+voting.name+ '\n para poder verlos sólamente tienes que acceder, dentro de la url de la app a "/visualizer/+' + str(voting.id)+'"'
            context = {'mensaje': mensaje, 'mail': correo}
            plantilla = get_template('plantilla_mail.html')
            content = plantilla.render(context)
            asunto = 'Resultados de votación DECIDE'
            email = EmailMultiAlternatives(asunto, content, settings.EMAIL_HOST_USER, [correo])
            email.fail_silently = False
            email.attach_alternative(content, 'text/html')
            email.send()


    def create_pubkey(self):
        if self.pub_key or not self.auths.count():
            return

        auth = self.auths.first()
        data = {
            "voting": self.id,
            "auths": [ {"name": a.name, "url": a.url} for a in self.auths.all() ],
        }
        key = mods.post('mixnet', baseurl=auth.url, json=data)
        pk = Key(p=key["p"], g=key["g"], y=key["y"])
        pk.save()
        self.pub_key = pk
        self.save()

    def get_votes(self, token=''):
        # gettings votes from store
        votes = mods.get('store', params={'voting_id': self.id}, HTTP_AUTHORIZATION='Token ' + token)
        # anon votes
        return [[i['a'], i['b']] for i in votes]

    def tally_votes(self, token=''):
        '''
        The tally is a shuffle and then a decrypt
        '''

        votes = self.get_votes(token)

        auth = self.auths.first()
        shuffle_url = "/shuffle/{}/".format(self.id)
        decrypt_url = "/decrypt/{}/".format(self.id)
        auths = [{"name": a.name, "url": a.url} for a in self.auths.all()]

        # first, we do the shuffle
        data = { "msgs": votes }
        response = mods.post('mixnet', entry_point=shuffle_url, baseurl=auth.url, json=data,
                response=True)
        if response.status_code != 200:
            # TODO: manage error
            pass

        # then, we can decrypt that
        data = {"msgs": response.json()}
        response = mods.post('mixnet', entry_point=decrypt_url, baseurl=auth.url, json=data,
                response=True)

        if response.status_code != 200:
            # TODO: manage error
            pass

        self.tally = response.json()
        self.save()

        self.do_postproc()

    def do_postproc(self):
        tally = self.tally
        questions = self.question.all()
        opts = []
        for question in questions:
            options = question.options.all()
            
            for opt in options:
                if isinstance(tally, list):
                    votes = tally.count(opt.number)
                else:
                    votes = 0
                opts.append({
                    'option': opt.option,
                    'number': opt.number,
                    'votes': votes
                })

        data = { 'type': 'IDENTITY', 'options': opts }
        postp = mods.post('postproc', json=data)

        self.postproc = postp
        self.save()
        
        self.enviar_correo()
        

    def __str__(self):
        return self.name
