import time
import random
from django.utils import timezone
from myapp.utils.rate_limiter import RateLimiter
from myapp.utils.idempotency import IdempotencyStore
from myapp.models import EmailStatus


class MockProviderA:
    def send_email(self, to, subject, body):
        if random.random() < 0.7:
            raise Exception("Provider A failed")
        return "Provider A: Email sent successfully"


class MockProviderB:
    def send_email(self, to, subject, body):
        if random.random() < 0.5:
            raise Exception("Provider B failed")
        return "Provider B: Email sent successfully"


class EmailService:
    def __init__(self):
        self.providers = [MockProviderA(), MockProviderB()]
        self.rate_limiter = RateLimiter(max_requests=5, interval=60)
        self.idempotency_store = IdempotencyStore()

    def send_email(self, to, subject, body, idempotency_key):
        if self.idempotency_store.exists(idempotency_key):
            return "Duplicate request ignored"

        if not self.rate_limiter.allow_request():
            return "Rate limit exceeded"

        attempt_status = EmailStatus.objects.create(
            to=to,
            subject=subject,
            status="pending",
            attempts=0
        )

        backoff = 1
        for attempt in range(3):
            for provider in self.providers:
                try:
                    attempt_status.attempts += 1
                    result = provider.send_email(to, subject, body)
                    attempt_status.status = "sent"
                    attempt_status.provider_used = provider.__class__.__name__
                    attempt_status.sent_at = timezone.now()
                    attempt_status.save()

                    self.idempotency_store.save(idempotency_key)
                    return result

                except Exception as e:
                    attempt_status.status = f"failed: {str(e)}"
                    attempt_status.save()

            time.sleep(backoff)
            backoff *= 2

        attempt_status.status = "permanently failed"
        attempt_status.save()
        return "All providers failed after retries"