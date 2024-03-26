from django.conf import settings
from rdflib import URIRef, Literal, Graph
from rdflib.namespace import RDF, FOAF
import requests
from bs4 import BeautifulSoup
from rest_framework import status
from rest_framework.response import Response
from uuid import uuid4
from .serializers import CrawlWebsiteSerializer
from rest_framework.views import APIView
from urllib.parse import urlparse, urljoin
from urllib.parse import quote
import re
                    
                    
class CrawlWebsiteView(APIView):
    serializer_class = CrawlWebsiteSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            url = serializer.validated_data['url']
            
        # Crawl the website
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Create a new graph
        g = Graph()

        # Your existing code...
        for link in soup.find_all('a'):
            href = link.get('href')
            if href is not None:
                href = urljoin(url, href)
                try:
                    result = urlparse(href)
                    if all([result.scheme, result.netloc]):
                        
                        # Remove or replace square brackets
                        href = re.sub(r'\[|\]', '', href)
                        
                        # Sanitize the href value
                        href = quote(href, safe="%/:=&?~#+!$,;'@()*[]")
                        
                        node = URIRef(f"http://example.com/resource/{uuid4()}")  # Create a unique URI for each node

                        # Add triples to the graph
                        g.add((node, RDF.type, FOAF.Document))
                        g.add((node, FOAF.title, Literal(link.text)))
                        g.add((node, FOAF.page, URIRef(href)))

                except ValueError:
                    continue

        # Serialize the graph to a string in N-Triples format
        data = g.serialize(format='nt')

        # Define the headers for the HTTP request
        headers = {
            'Content-Type': 'application/x-turtle',
        }

        # Define the URL for the HTTP request
        url = f"http://{settings.GRAPHDB['HOST']}:{settings.GRAPHDB['PORT']}/repositories/{settings.GRAPHDB['REPOSITORY']}/statements"

        # Send the data to GraphDB
        response = requests.post(url, headers=headers, data=data.encode('utf-8'))

        # Check the response
        if response.status_code != 204:
            print(f"Error: {response.text}")
        else:
            print("Data added successfully")
            
        return Response(status=status.HTTP_201_CREATED)