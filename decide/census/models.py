from django.db import models
from django.contrib.auth.models import User
from voting.models import Voting

class Census(models.Model):
    name = models.CharField(max_length=50, default='')
    voting_id = models.ForeignKey(Voting,on_delete=models.CASCADE)
    voter_id= models.ManyToManyField(User)

    class Meta:
        unique_together = (('name'),('voting_id'),)
        
    def __str__(self):
        return self.name

