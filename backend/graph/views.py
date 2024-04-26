from django.conf import settings
from rdflib import URIRef, Literal, Graph
from rdflib.namespace import RDF, FOAF
import requests
from bs4 import BeautifulSoup
from rest_framework import status
from rest_framework.response import Response
from uuid import uuid4
from .serializers import CrawlWebsiteSerializer, SearchYAGOSerializer
from rest_framework.views import APIView
from urllib.parse import urlparse, urljoin
from urllib.parse import quote
import re

class SearchYAGOView(APIView):
    serializer_class = SearchYAGOSerializer
    
    def post(self, request):
        # Get the query from the serializer
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        query_param = serializer.validated_data['year']
        limit = serializer.validated_data['limit']
        lang = serializer.validated_data['lang']
        offset = serializer.validated_data['offset']

        # Define the URL for the HTTP request
        url = "https://yago-knowledge.org/sparql/query"

        # Define the SPARQL query
        query = f"""
        PREFIX yago: <http://yago-knowledge.org/resource/>
        SELECT ?s ?p ?o
        WHERE {{
            ?s ?p ?o .
            FILTER regex(?o, "{query_param}", "i")
            FILTER langMatches(lang(?o), "{lang}")
        }}
        LIMIT {limit}
        OFFSET {offset}
        """

        # Define the headers for the HTTP request
        headers = {
            'Accept': 'application/sparql-results+json',
            'Content-Type': 'application/sparql-query',
        }

        # Send the SPARQL query to API
        try:
            response = requests.post(url, headers=headers, data=query.encode('utf-8'), timeout=60)
            response.raise_for_status()  # Raise an exception if the request failed
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Parse the results
        results = response.json()

        # Define the URL for the GraphDB query endpoint
        graphdb_query_url = f"http://{settings.GRAPHDB['HOST']}:{settings.GRAPHDB['PORT']}/repositories/{settings.GRAPHDB['REPOSITORY']}"

        # Define the URL for the GraphDB update endpoint
        graphdb_update_url = f"http://{settings.GRAPHDB['HOST']}:{settings.GRAPHDB['PORT']}/repositories/{settings.GRAPHDB['REPOSITORY']}/statements"

        # Define the headers for the GraphDB request
        graphdb_headers = {
            'Content-Type': 'application/sparql-update',
        }
        
        graphdb_ask_headers = {
            'Content-Type': 'application/sparql-query',
        }

        # Insert the results into GraphDB
        for result in results['results']['bindings']:
            s = result['s']['value']
            p = result['p']['value']
            o = result['o']['value']
            
            # Get the year from the serializer
            year = query_param
            
            # Calculate the century from the year
            century = (int(year) - 1) // 100 + 1

            # Define the SPARQL ASK query
            ask_query = f"""
            ASK {{
                <{s}> <{p}> "{o}" .
            }}
            """

            # Send the SPARQL ASK query to GraphDB
            try:
                response = requests.post(graphdb_query_url, headers=graphdb_ask_headers, data=ask_query.encode('utf-8'))  # Use the query URL here
                response.raise_for_status()  # Raise an exception if the request failed
            except requests.exceptions.RequestException as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the triple already exists in the database
            if response.json()['boolean']:
                continue  # Skip this triple

            # Define the SPARQL update query
            update_query = f"""
            INSERT DATA {{
                <{s}> <{p}> "{o}" .
                <{s}> a <http://example.com/Event> .
                <http://example.com/{year}> a <http://example.com/Year> .
                <http://example.com/{century}> a <http://example.com/Century> .
                <{s}> <http://example.com/hasYear> <http://example.com/{year}> .
                <http://example.com/{year}> <http://example.com/hasCentury> <http://example.com/{century}> .
            }}
            """
            
            # Send the SPARQL update query to GraphDB
            try:
                response = requests.post(graphdb_update_url, headers=graphdb_headers, data=update_query.encode('utf-8'))  # Use the update URL here
                response.raise_for_status()  # Raise an exception if the request failed
            except requests.exceptions.RequestException as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(results, status=status.HTTP_200_OK)
                    

## DEPRICATED                
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