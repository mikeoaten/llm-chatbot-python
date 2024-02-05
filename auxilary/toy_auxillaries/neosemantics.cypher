// https://neo4j.com/labs/neosemantics/4.3/config/
// Import RDF data

// The method n10s.graphconfig.init can help us with this setup. Calling the procedure without parameters will set all the default values:
CALL n10s.graphconfig.init();

// The Graph Configuration can be removed by invoking and then reloading/refreshing the browser
CALL n10s.graphconfig.drop

// Current set up listed with
CALL n10s.graphconfig.show

// List namespaces
CALL n10s.nsprefixes.list

// All methods that persist data into Neo4j have a schema level pre-requisite: this is the existence of a uniqueness constraint on the property uri of nodes with the label Resource. If the constraint is not present yet, all you need to do is run the following command on your DB, otherwise all RDF-importing procedures will throw an error message indicating this has to be done first.
CREATE CONSTRAINT n10s_unique_uri FOR (r:Resource)
REQUIRE r.uri IS UNIQUE;

// If you’re working on a windows machine and want to access an RDF file stored on your drive, here’s the syntax for paths:
//CALL n10s.rdf.import.fetch("file:///D:\\Data\\some_rdf_file.rdf", "RDF/XML");

// preview/import of an open calais output
CALL n10s.rdf.preview.fetch("file: ///C:\\Users\\mikej\\Documents\\GitHub\\llm-chatbot-python\\build_ontology\\open_calais_test.xml", "RDF/XML");

// to clear out all RDF data from the graph
MATCH (n:Resource)
DETACH DELETE n;

// Imported an RDF ontology into Neo4j
// https://neo4j.com/labs/neosemantics/4.3/importing-ontologies/
// n.b. graphconfig.init() and constraints must be run first
CALL n10s.onto.import.fetch("file: ///C:\\Users\\mikej\\Documents\\GitHub\\llm-chatbot-python\\build_ontology\\onecalais.owl.allmetadata.xml", "RDF/XML");

// Create MAPPED_TO relationships between the imported data and the ontology
MATCH (m:Resource)
WHERE m.uri STARTS //s.opencalais.com/1/type/em/e/'
WITH 'http:
 OR m.uri STARTS //s.opencalais.com/1/type/em/r/'
WITH 'http:
 OR m.uri STARTS //s.opencalais.com/1/type/er/'
WITH 'http:
 OR m.uri STARTS //s.opencalais.com/1/type/er/Geo/'
WITH 'http:
WITH m, split(m.uri, '/') AS parts
MATCH (n)
WHERE 'ns7__' + last(parts) IN labels(n)
 OR 'ns5__' + last(parts) IN labels(n)
 OR 'ns6__' + last(parts) IN labels(n)
 OR 'ns8__' + last(parts) IN labels(n)
MERGE (n)-[:MAPPED_TO]->(m)
RETURN
m, n;

// Created MATCHED_TO relationships between rns Companies and Open Calais Compnaies
MATCH (c1:Company)
MATCH (c2: ns6__Company)
WHERE c1.tidm = c2.ns0__ticker
MERGE (c1)-[:MATCHED_TO]->(c2);
