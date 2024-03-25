from rest_framework import serializers

class CrawlWebsiteSerializer(serializers.Serializer):
    url = serializers.URLField()