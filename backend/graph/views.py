from django.conf import settings
from rdflib import URIRef, Literal
from rdflib.namespace import RDF, FOAF
import requests
from bs4 import BeautifulSoup
from rest_framework import status
from rest_framework.response import Response
from rdflib.store import Store
from rdflib.plugin import get as plugin_get
from rdflib import ConjunctiveGraph
from uuid import uuid4
from .serializers import CrawlWebsiteSerializer
from rest_framework.views import APIView
from urllib.parse import urlparse, urljoin
from SPARQLWrapper import SPARQLWrapper, POST

class CrawlWebsiteView(APIView):
    serializer_class = CrawlWebsiteSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            url = serializer.validated_data['url']

            # Crawl the website
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Create a new SPARQLWrapper instance
            sparql = SPARQLWrapper(f"http://{settings.GRAPHDB['HOST']}:{settings.GRAPHDB['PORT']}/repositories/{settings.GRAPHDB['REPOSITORY']}")
            

            # Parse the crawled data and convert it into RDF triples
            for link in soup.find_all('a'):
                href = link.get('href')
                if href is not None:
                    href = urljoin(url, href)
                    try:
                        result = urlparse(href)
                        if all([result.scheme, result.netloc]):
                            node = f"http://example.com/resource/{uuid4()}"  # Create a unique URI for each node

                            # Define SPARQL UPDATE queries
                            queries = [
                                f"""
                                INSERT DATA {{
                                    <{node}> a <http://xmlns.com/foaf/0.1/Document> .
                                }}
                                """,
                                f"""
                                INSERT DATA {{
                                    <{node}> <http://xmlns.com/foaf/0.1/title> "{link.text}" .
                                }}
                                """,
                                f"""
                                INSERT DATA {{
                                    <{node}> <http://xmlns.com/foaf/0.1/page> <{href}> .
                                }}
                                """
                            ]
                            sparql.method = POST
                            sparql.queryType = 'UPDATE'
                            # Send the SPARQL UPDATE queries
                            for query in queries:
                                print(query)
                                sparql.setQuery(query)
                                sparql.query()
                    except ValueError:
                        continue


# class CrawlWebsiteView(APIView):
#     serializer_class = CrawlWebsiteSerializer

#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#         if serializer.is_valid():
#             url = serializer.validated_data['url']

#             # Crawl the website
#             response = requests.get(url)
#             soup = BeautifulSoup(response.text, 'html.parser')

#             # Create a new RDF graph
#             # store = plugin_get('SPARQLUpdateStore', Store)()
#             g = ConjunctiveGraph('SPARQLStore')
#             g.open(f"http://{settings.GRAPHDB['HOST']}:{settings.GRAPHDB['PORT']}/repositories/{settings.GRAPHDB['REPOSITORY']}")

#             # Parse the crawled data and convert it into RDF triples
#             for link in soup.find_all('a'):
#                 href = link.get('href')
#                 if href is not None:
#                     href = urljoin(url, href)
#                     try:
#                         result = urlparse(href)
#                         if all([result.scheme, result.netloc]):
#                             node = URIRef(f"http://example.com/resource/{uuid4()}")  # Create a unique URI for each node
#                             g.add((node, RDF.type, FOAF.Document))  # The node is a foaf:Document
#                             g.add((node, FOAF.title, Literal(link.text)))  # The document's title is the link text
#                             g.add((node, FOAF.page, URIRef(href)))  # The document's page is the link URL
#                     except ValueError:
#                         continue
#             # Write the RDF triples to GraphDB
#             g.commit()

#             return Response({'status': 'success'})
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

