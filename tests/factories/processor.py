import factory
from django.utils import timezone

from dook.core.processor.models import NewsDraft


class NewsDraftFactory(factory.DjangoModelFactory):
    class Meta:
        model = NewsDraft

    url = factory.Faker("uri")
    screenshot_url = factory.Faker("uri")
    reporter_email = factory.Faker("email")
    reported_at = factory.LazyFunction(timezone.now)
    text = factory.Faker("text")
    comment = factory.Faker("sentence")
