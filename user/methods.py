from django.utils import timezone

import random
import string
import re
from datetime import timedelta


def generate_activation_code():
    # Generate a group of 4 random uppercase letters.
    letters = lambda: ''.join(random.choices(string.ascii_uppercase, k=4))
    # Generate a group of 4 random digits.
    digits = lambda: ''.join(random.choices(string.digits, k=4))

    # Combine segments into the format: letters-digits-letters-digits.
    return f"{letters()}-{digits()}-{letters()}-{digits()}"


def remain_secs(value):
    """
    Calculate the number of seconds remaining between a given time and now.

    The input `value` can either be:
      - A datetime object: The method calculates the difference between this datetime and the current time.
      - A string in the format "[-]Xd HH:MM:SS": like 2d 22:02:13
    """

    # If value is a string, try to parse it into a datetime based on the expected format.
    if isinstance(value, str):
        # Define regex to match an optional negative sign, days, and a time component (HH:MM:SS)
        pattern = r'^(-?)(\d+)d\s+(\d{1,2}):(\d{1,2}):(\d{1,2})$'
        match = re.match(pattern, value)
        if match:
            # Extract the sign, days, hours, minutes, and seconds from the string.
            sign_str, days_str, hours_str, mins_str, secs_str = match.groups()
            # Determine if the offset should be added (positive) or subtracted (negative)
            sign = -1 if sign_str == "-" else 1
            # Create a timedelta with the parsed values.
            delta = timedelta(
                days=int(days_str),
                hours=int(hours_str),
                minutes=int(mins_str),
                seconds=int(secs_str)
            )
            now = timezone.now()
            # Compute the target datetime by subtracting or adding the timedelta from now.
            value = now - delta if sign < 0 else now + delta
        else:
            # If the string doesn't match the expected format, return it unchanged.
            return value

    # At this point, value should be a datetime object.
    now = timezone.now()
    # Calculate the difference (as a timedelta) between the target time and now.
    delta = value - now
    # Convert the timedelta to a total number of seconds (rounded to an integer).
    total_seconds = int(delta.total_seconds())
    return total_seconds