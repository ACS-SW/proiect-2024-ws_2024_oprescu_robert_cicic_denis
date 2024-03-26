# Semantic Web Crawler API (With GraphDB) for Ontologically Related Data
This application provides a simple API for crawling a website and extracting all the links (anchor tags) from it.

## Setup
Fork and clone this repo onto your machine and execute:        
  -  `$ cd backend`
  -  `$ docker-compose up`
  -  `docker-compose exec web python manage.py migrate`

Set up GraphDB repository by going to `localhost:7200 --> Setup --> Repositories --> Create new repository --> GraphDB repository --> Repository ID*: main-repo, Ruleset: RDFS --> Create --> Click the "connect" button on main-repo`

## Features
Crawl Website: The API provides an endpoint (/api/crawl/) that accepts a POST request with a URL in the request body. The application will then crawl the website at the given URL and extract all the links from it.
How It Works
When a POST request is made to the /api/crawl/ endpoint, the application sends a GET request to the URL provided in the request body. It then parses the response using BeautifulSoup to extract all the anchor tags from the HTML.

For each anchor tag, the application extracts the href attribute and uses it to create a new IRI (Internationalized Resource Identifier). The application also creates a new node in a graph for each IRI, and adds triples to the graph that represent the IRI's type, title, and page.

The application sanitizes the href values before using them to create IRIs. It removes or replaces any characters that are not allowed in IRIs, such as square brackets.

## Future Work
This is a basic implementation of a web crawler, and there are many ways it could be expanded. For example, the application could be modified to crawl multiple pages of a website, or to extract additional information from each page. It could also be integrated with a database or a search engine to store and search the extracted links.
