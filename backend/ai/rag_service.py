class EngineeringRAG:
    """Simple local adapter; replace storage with pgvector/Qdrant later."""

    def __init__(self):
        self.documents = []

    def add_document(self, name, text):
        self.documents.append({"name": name, "text": text})

    def search(self, query, limit=5):
        terms = set(query.lower().split())
        scored = []
        for doc in self.documents:
            words = set(doc["text"].lower().split())
            scored.append((len(terms & words), doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored[:limit] if score > 0]

rag = EngineeringRAG()
