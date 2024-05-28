from rest_framework import serializers

class CrawlWebsiteSerializer(serializers.Serializer):
    url = serializers.URLField()
    
class SearchYAGOSerializer(serializers.Serializer):
    LANG_CHOICES = [
        ('en', 'English'),
        ('de', 'German'),
        ('fr', 'French'),
        # Add more languages as needed
    ]
    
    year = serializers.IntegerField()
    limit = serializers.IntegerField()
    lang = serializers.ChoiceField(choices=LANG_CHOICES)
    offset = serializers.IntegerField(default=0)
    
class BulkUploadSerializer(serializers.Serializer):
    file = serializers.FileField()