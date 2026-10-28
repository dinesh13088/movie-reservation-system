
# views.py
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import MoviesSerializer
from .scraper.scrape_movies import scrape_movies

class MovieDetails(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            movies_list = scrape_movies()
            print(f"Movies list: {movies_list}")  # DEBUG
            
            if not movies_list:
                return Response({"error": "No movies found"}, status=404)
            
            serializer = MoviesSerializer(movies_list, many=True)
            return Response(serializer.data)
        except Exception as e:
            print(f"API Error: {e}")  # DEBUG
            return Response({
                "error": "Failed to fetch movie details", 
                "debug_message": str(e)
            }, status=500)
