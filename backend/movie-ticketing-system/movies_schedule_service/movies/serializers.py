from rest_framework import serializers


class MoviesSerializer(serializers.Serializer):
    Title = serializers.CharField()
    Image_URL = serializers.CharField()
    Rating = serializers.CharField(allow_blank=True)
    Language = serializers.CharField(allow_blank=True)
    Genres = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    Genre_language = serializers.CharField(allow_blank=True)