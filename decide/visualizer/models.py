from django.db import models

class Mail(models.Model):
    mail=models.EmailField()
    voting_id=models.IntegerField()

    class Meta:
        unique_together = (('mail'),('voting_id'),)
        
    def __str__(self):
        return self.mail +'/'+ str(self.voting_id)
