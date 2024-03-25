from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CrawlWebsiteView

router = DefaultRouter()
# router.register(r'crawl', CrawlWebsiteViewSet, basename='crawl_website')

urlpatterns = [
    path('', include(router.urls)),
    path('crawl/', CrawlWebsiteView.as_view(), name='crawl_website'),    
]