from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

class RAGSystem:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vector_store = None
        self.initialize_vector_store()
        
    def initialize_vector_store(self):
        if os.path.exists("vector_store"):
            self.vector_store = FAISS.load_local("vector_store", self.embeddings)
        else:
            # Initialize with empty documents if no existing store
            self.vector_store = FAISS.from_texts(
                ["Initial document"], self.embeddings
            )
            
    def add_to_knowledge(self, text):
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_text(text)
        self.vector_store.add_texts(chunks)
        self.vector_store.save_local("vector_store")
        
    def retrieve_relevant_context(self, query, k=3):
        docs = self.vector_store.similarity_search(query, k=k)
        return "\n".join([doc.page_content for doc in docs]) 