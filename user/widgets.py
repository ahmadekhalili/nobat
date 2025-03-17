# user/widgets.py
import re
from datetime import timedelta
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .methods import remain_secs

import jdatetime


class RemainingTimeWidget(forms.TextInput):
    """
    A widget that:
      - Displays expiration_date as 'X d HH:MM:SS' or '-X d HH:MM:SS' from now.
      - Color-codes the text (red if in the past, green if in the future).
      - Parses user input back into a Python datetime.
    """

    def format_value(self, value):
        # Convert a datetime value into a string like '-2d 03:12:00' or '30d 05:10:00'.
        if not value:
            return ""

        total_seconds = remain_secs(value)
        sign_str = "-" if total_seconds < 0 else ""
        abs_seconds = abs(total_seconds)

        days = abs_seconds // 86400
        remainder = abs_seconds % 86400
        hours = remainder // 3600
        remainder %= 3600
        minutes = remainder // 60
        secs = remainder % 60

        # Return something like '-2d 03:12:00' or '30d 05:10:00'
        return f"{sign_str}{days}d {hours:02d}:{minutes:02d}:{secs:02d}"

    def value_from_datadict(self, data, files, name):
        raw_value = data.get(name, "").strip()
        if not raw_value:
            return None

        pattern_h = r'^(-?\d+)d$'
        if re.match(pattern_h, raw_value):   # if raw value is ONLY DATE: 2d or 200d -10d 0d or... (without time)
            raw_value = f'{raw_value} 00:00:00'
        pattern = r'^(-?)(\d+)(?:d\s+)?(\d{1,2}):(\d{1,2}):(\d{1,2})$'
        match = re.match(pattern, raw_value)
        if not match:
            raise ValidationError("Invalid format. Correct example: '30d 05:00:00' or '-2d 03:12:00'.")

        sign_str, days_str, hours_str, mins_str, secs_str = match.groups()
        sign = -1 if sign_str == "-" else 1

        delta = timedelta(
            days=int(days_str),
            hours=int(hours_str),
            minutes=int(mins_str),
            seconds=int(secs_str)
        )

        now = timezone.now()
        target_datetime = now - delta if sign < 0 else now + delta
        # target_datetime_naive = target_datetime.replace(tzinfo=None)
        jd = jdatetime.datetime.fromgregorian(datetime=target_datetime)
        return jd.strftime("%Y-%m-%d %H:%M:%S")

    def render(self, name, value, attrs=None, renderer=None):
        """
        Render the <input> tag, color-coded based on whether expiration_date is in the future or past.
        """
        if value:
            now = timezone.now()
            delta = value - now
            color = "red" if delta.total_seconds() < 0 else "green"
        else:
            color = "black"

        # Convert the datetime into our custom "Xd HH:MM:SS" format
        str_value = self.format_value(value)

        # Build final attrs, including style for color-coded text
        final_attrs = self.build_attrs(
            attrs, 
            {
                'type': 'text',
                'name': name,
                'value': str_value,
                'style': f'color:{color};'
            }
        )
        return super().render(name, str_value, final_attrs, renderer=renderer)
