from django.contrib.auth.hashers import BasePasswordHasher
from django.utils.crypto import constant_time_compare

class PlainTextPasswordHasher(BasePasswordHasher):
    algorithm = "plain"

    def salt(self):
        # No salt is used because we are storing plaintext
        return ''

    def encode(self, password, salt):
        # Return the password in a predictable format
        return f"{self.algorithm}${password}"

    def verify(self, password, encoded):
        algorithm, original = encoded.split('$', 1)
        return constant_time_compare(password, original)

    def safe_summary(self, encoded):
        algorithm, original = encoded.split('$', 1)
        return {
            "algorithm": algorithm,
            "password": original,
        }
