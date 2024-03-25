import psycopg2
from langchain.vectorstores.pgvector import PGVector
from langchain_community.embeddings import OllamaEmbeddings

# vector store backed retriever doc: https://python.langchain.com/docs/modules/data_connection/retrievers/vectorstore

class VectorRetriever:
    def __init__(self, conn_string: str, collection: str):
        self.conn_string = conn_string
        self.collection = collection
        self.embeddings = OllamaEmbeddings(model="llama2")

        self.store = PGVector(
            collection_name=self.collection,
            connection_string=self.conn_string,
            embedding_function=self.embeddings
        )
    
    def get_docs(self, query: str, k=5, fetch_k=10):
        result = self.store.max_marginal_relevance_search(query, k=k, fetch_k=fetch_k)
        return result
    
    def get_context(self):
        conn = psycopg2.connect(self.conn_string)
        cur = conn.cursor()
        cur.execute("SELECT document FROM langchain_pg_embedding")
        docs = cur.fetchall()

        cur.close()
        conn.close()

        return docs