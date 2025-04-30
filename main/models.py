from django.db import models

from django.dispatch import receiver
from django.db.models.signals import pre_save

import pytz
import jdatetime

from .socket_methods import update_browser_status





class OpenedBrowser(models.Model):
    driver_id = models.IntegerField(null=True, blank=True)
    driver_number = models.IntegerField(default=0, blank=True)  # only 1,2,3
'''
# this is for socket channels (change browser icon, when job status get 'finish'
@receiver(pre_save, sender=Job)
def notify_finish_status(sender, instance, **kwargs):
    # send job.status to the websocket if changed to 'finish' to update browser icon
    if not instance.driver_process_id:
        return

    # دستور: رکورد جدید که مستقیماً finish ست شده
    if instance._state.adding and instance.status == 'finish':
        update_browser_status({str(instance.driver_process_id): instance.status})
        return

    # دستور: رکورد موجود—وضعیت قبلی رو از دیتابیس بگیر
    old_status = sender.objects.filter(pk=instance.pk).values_list('status', flat=True).first()
    # send through socketunnel
    if old_status != 'finish' and instance.status == 'finish':
        # send finally as {'statuses': {str(instance.driver_process_id): instance.status}} by consumers.py
        update_browser_status({str(instance.driver_process_id): instance.status})
'''