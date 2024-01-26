import spacy

nlp = spacy.load(
    "en_core_web_sm",
    disable=["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer"],
)

ner = nlp.get_pipe("ner")

# # Get the labels and their definitions
# labels_and_defs = {label: spacy.explain(label) for label in ner.labels}

# # Print the labels and their definitions
# for label, definition in labels_and_defs.items():
#     print(f"{label}: {definition}")

doc = nlp(
    """
	Following the sale of Shares, Janet Pope continues to comply with the Group's shareholding policy requirements..
    """
)

for ent in doc.ents:
    print(ent.text, ent.start_char, ent.end_char, ent.label_)
