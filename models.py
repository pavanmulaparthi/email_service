from django.db import models

class EmailStatus(models.Model):
    to = models.EmailField()
    subject = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    attempts = models.IntegerField(default=0)
    provider_used = models.CharField(max_length=50, null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)