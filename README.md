# Semantic Historical Record Query Tool (With GraphDB) for Ontologically Related Data
This application provides a simple API for interacting with historical data in a semantically meaningful way using RDF graphs.

## Setup
Fork and clone this repo onto your machine and execute:        
  -  `$ cd backend`
  -  `$ docker-compose up`
  -  `$ docker-compose exec web python manage.py migrate`

Set up GraphDB repository by going to `localhost:7200 --> Setup --> Repositories --> Create new repository --> GraphDB repository --> Repository ID*: main-repo, Ruleset: RDFS --> Create --> Click the "connect" button on main-repo`

## Features
- (new) Bulk upload now lets you upload a turtle file at `/api/upload/` and will generate the ontology by extracting the years and calculating the centuries for the entire file
- (new) Downloading all triples from GraphDB is now available in rdf format at `/api/download/`
- Search historical events by year, at "/api/search/". This endpoint allows you to set limit for the number of triples (10 to 20 is recommended), language and offset (number of triples skipped from the beginning of the response)
- Visualize data by going to `localhost:7200/graphs --> The default graph --> select a resource (try selecting a year or century of rdf:type) then click Visual graph and then expand the nodes`, `localhost:7200/relationships` or `localhost:7200/hierarchy`
- (Deprecated) Crawl Website: The API provides an endpoint (/api/crawl/) that accepts a POST request with a URL in the request body. The application will then crawl the website at the given URL and extract all the links from it.

### How it works
A POST request to /api/search/ will make a SPARQL request to `https://yago-knowledge.org/sparql/query` and retrieve a number of triples containing the number in the field "year", then it will write them to the GraphDB database including attributes `hasYear`, and for the year `hasCentury` thus establishing an ontology based on historical markers (years and centuries).

### How It Works (Deprecated)
When a POST request is made to the /api/crawl/ endpoint, the application sends a GET request to the URL provided in the request body. It then parses the response using BeautifulSoup to extract all the anchor tags from the HTML.

For each anchor tag, the application extracts the href attribute and uses it to create a new IRI (Internationalized Resource Identifier). The application also creates a new node in a graph for each IRI, and adds triples to the graph that represent the IRI's type, title, and page.

The application sanitizes the href values before using them to create IRIs. It removes or replaces any characters that are not allowed in IRIs, such as square brackets and then stores the information in the GraphDB database.

## Future Work
The addition of multiple historical markers as ontological attributes is a focus. Also we'd like to add an endpoint for downloading RDF schemas based on ranges of those markers (years, centuries), with a limit to the number of triples. (e.g from: 1995, to: 2005, limit: 100)
