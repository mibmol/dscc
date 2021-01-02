from django.db import models


class Notification(models.Model):
    title = models.CharField(max_length=100)
    body = models.CharField(max_length=1000)
    data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey("users.user", on_delete=models.DO_NOTHING, null=True)
    seen = models.BooleanField(default=False)
    is_broadcast = models.BooleanField(default=False)
