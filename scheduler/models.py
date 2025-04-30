from django.db import models
from django.conf import settings
from django.db import models

import pytz


class CrawlFuncArgs(models.Model):
    customer_id = models.IntegerField(null=True, blank=True)
    reserve_date = models.CharField(max_length=30, blank=True)  # reservation time
    reserve_time = models.CharField(max_length=30, blank=True)
    is_test = models.BooleanField(default=True)
    #title_ids = models.TextField(blank=True)  # sims useless, structure: 1a,1b,2a,2b

    def get_reserve_dates_times(self):
        dates, times = [], []
        if self.reserve_date:
            dates.append(self.reserve_date)
        if self.reserve_time:
            times.append()
        return dates, times


class Job(models.Model):  # every process one job
    # id auto
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, db_index=True, default='wait', blank=True, choices=[('wait', 'Wait'), ('finish', 'Finish'), ('close', 'Close')])  # wait, finish, close
    func_args = models.ForeignKey(CrawlFuncArgs, on_delete=models.CASCADE, null=True, blank=True)
    process_id = models.IntegerField(null=True, blank=True)  # used to kill python process if needed
    driver_process_id = models.IntegerField(null=True, blank=True)  # used to get hwnd to control window

    class Meta:
        ordering = ['-start_time']  # Newest first (oldest last)

    @property
    def start_time_persian(self):
        """Returns start_time in Asia/Tehran time as naive datetime (if USE_TZ=False)."""
        tehran_tz = pytz.timezone(settings.TIME_ZONE)
        if self.start_time.tzinfo:
            # If datetime is timezone-aware
            return self.start_time.astimezone(tehran_tz)
