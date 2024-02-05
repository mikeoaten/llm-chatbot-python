import spacy
import textacy
import matplotlib.pylab as plt
import networkx as nx

nlp = spacy.load(
    "en_core_web_sm",
    # disable=["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer"],
)

# ner = nlp.get_pipe("ner")

# # Get the labels and their definitions
# labels_and_defs = {label: spacy.explain(label) for label in ner.labels}

# # Print the labels and their definitions
# for label, definition in labels_and_defs.items():
#     print(f"{label}: {definition}")

doc = nlp(
    """
Supplementary Prospectus dated 5 May 2023 (the "Supplementary Prospectus") relating to the £25,000,000,000 Euro Medium Term Note Programme of Lloyds Banking Group plc.
    """
)

# for ent in doc.ents:
#     print(ent.text, ent.start_char, ent.end_char, ent.label_)

# Extract SVO list from spacy object
triples = list(textacy.extract.subject_verb_object_triples(doc))
print(triples)
# [SVOTriple(subject=[I], verb=[am, going], object=[to, extract, SVO])]

# Extract SVO graph from spacy object
nodes = []
relations = []
# iterate over the triples
for triple in triples:
    # extract the Subject and Object from triple
    node_subject = "_".join(map(str, triple.subject))
    node_object = "_".join(map(str, triple.object))
    nodes.append(node_subject)
    nodes.append(node_object)
    # extract the relation between S and O
    # add the attribute 'action' to the relation
    relation = "_".join(map(str, triple.verb))
    relations.append((node_subject, node_object, {"action": relation}))
# remove duplicate nodes
nodes = list(set(nodes))
print(nodes)
# ['to_extract_SVO', 'I']
print(relations)
# [('I', 'to_extract_SVO', {'action': 'am_going'})]
