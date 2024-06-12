import pandas as pd
from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD
from tqdm import tqdm

# Define the namespaces
ex = Namespace("https://www.olympics.com/athletes/")
ao = Namespace("http://www.olympics.com/ontology/ao/")

# Create a new RDF graph
g = Graph()

# Bind the namespaces to the graph
g.bind("ex", ex)
g.bind("ao", ao)

# Define a function to modify URIs
def modify_uri(uri):
    if pd.isna(uri):
        return "unknown"
    else:
        modified_uri = uri.replace(" ", "_").replace('"', '').replace("`", "")
        return modified_uri

# Load the dataset into a pandas DataFrame
df = pd.read_csv('athlete_events.csv')

# Iterate over the DataFrame rows
for index, row in tqdm(df.iterrows(), total=len(df), desc="Processing rows"):
    modified_athlete_uri = URIRef(ex + modify_uri(row['Name']))
    modified_team_uri = URIRef(ex + modify_uri(row['Team']))
    modified_event_uri = URIRef(ex + modify_uri(row['Event']))
    modified_games_uri = URIRef(ex + modify_uri(row['Games']))
    modified_sport_uri = URIRef(ex + modify_uri(row['Sport']))
    modified_city_uri = URIRef(ex + modify_uri(row['City']))

    g.add((modified_athlete_uri, RDF.type, ao.Athlete))
    g.add((modified_athlete_uri, ao.sex, Literal(row['Sex'])))
    g.add((modified_athlete_uri, ao.age, Literal(row['Age'], datatype=XSD.integer)))
    g.add((modified_athlete_uri, ao.height, Literal(row['Height'], datatype=XSD.float)))
    g.add((modified_athlete_uri, ao.weight, Literal(row['Weight'], datatype=XSD.float)))
    g.add((modified_athlete_uri, ao.team, modified_team_uri))
    g.add((modified_athlete_uri, ao.noc, Literal(row['NOC'])))
    g.add((modified_athlete_uri, ao.games, modified_games_uri))
    g.add((modified_athlete_uri, ao.year, Literal(row['Year'], datatype=XSD.integer)))
    g.add((modified_athlete_uri, ao.season, Literal(row['Season'])))
    g.add((modified_athlete_uri, ao.city, modified_city_uri))
    g.add((modified_athlete_uri, ao.sport, modified_sport_uri))
    g.add((modified_athlete_uri, ao.event, modified_event_uri))
    g.add((modified_athlete_uri, ao.medal, Literal(row['Medal'])))


# Save the graph to an RDF file
g.serialize(destination='athlete_events.rdf', format='xml')