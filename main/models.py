from django.db import models


class Job(models.Model):  # every process one job
    # id auto
    name = models.CharField(max_length=100, blank=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True)
    customer_id = models.IntegerField(null=True, blank=True)
    is_test = models.BooleanField(default=True)
    title_ids = models.TextField(blank=True)      # structure: 12313,321313,534534

