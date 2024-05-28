from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CrawlWebsiteView, SearchYAGOView, DownloadRDFView, BulkUploadView

router = DefaultRouter()
# router.register(r'crawl', CrawlWebsiteViewSet, basename='crawl_website')

urlpatterns = [
    path('', include(router.urls)),
    path('crawl/', CrawlWebsiteView.as_view(), name='crawl_website'),    
    path('search/', SearchYAGOView.as_view(), name='search_yago'),
    path('download/', DownloadRDFView.as_view(), name='download_rdf'),
    path('upload/', BulkUploadView.as_view(), name='bulk_upload'),
]