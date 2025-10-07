# Import all test classes to ensure they're discovered by Django's test runner
from .test_admin import AdAnalyticsAdminTest
from .test_models import AdClickModelTest, AdImpressionModelTest, AdModelTest
from .test_services import AdSelectionServiceTest
from .test_views import AdClickViewTest

__all__ = [
    "AdModelTest",
    "AdImpressionModelTest",
    "AdClickModelTest",
    "AdSelectionServiceTest",
    "AdClickViewTest",
    "AdAnalyticsAdminTest",
]
