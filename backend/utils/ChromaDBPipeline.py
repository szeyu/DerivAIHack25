import chromadb
from chromadb.config import Settings
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
import os
import shutil

load_dotenv()

class ChromaDBPipeline:
    """Pipeline for loading PDFs, creating a ChromaDB vector store, and retrieving stored chunks."""

    def __init__(self, data_dir: str, db_dir: str):
        self.data_dir = data_dir
        self.db_dir = db_dir
        self.client = chromadb.PersistentClient(path=self.db_dir)

    def load_and_process_pdfs(self):
        """Load PDFs from directory and split into chunks."""
        print("📄 Loading and processing PDFs...")
        loader = DirectoryLoader(
            self.data_dir,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader
        )
        documents = loader.load()

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        chunks = text_splitter.split_documents(documents)
        print(f"✅ Created {len(chunks)} chunks from PDFs.")
        return chunks

    def create_vector_store(self, chunks):
        """Create and persist Chroma vector store."""
        # Clear existing vector store if it exists
        if os.path.exists(self.db_dir):
            print(f"🧹 Clearing existing vector store at {self.db_dir}")
            shutil.rmtree(self.db_dir)

        # Initialize HuggingFace embeddings
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2",
            model_kwargs={'device': 'cpu'}
        )

        # Create and persist Chroma vector store
        print("🚀 Creating new vector store...")
        vectordb = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=self.db_dir
        )
        print(f"✅ Vector store created and persisted at {self.db_dir}.")
        return vectordb

    def access_chroma_objects(self):
        """Retrieve all ChromaDB collections and stored chunks."""
        print("\n🔍 Accessing ChromaDB Objects...")

        # Get all collection names
        collection_names = self.client.list_collections()
        print(f"📁 Found {len(collection_names)} collections in ChromaDB:")

        for collection_name in collection_names:
            print(f"🔹 Collection Name: {collection_name}")

            # Get the actual collection
            collection = self.client.get_collection(collection_name)

            # Retrieve all stored documents and metadata
            all_data = collection.get()

            print(f"📜 Found {len(all_data['documents'])} stored chunks in '{collection_name}':")
            
            # Print stored chunks and metadata
            for idx, document in enumerate(all_data['documents']):
                print(f"\nChunk {idx+1}: {document}")
                
            if 'metadatas' in all_data and all_data['metadatas']:
                print("\n🔖 Metadata:")
                for metadata in all_data['metadatas']:
                    print(metadata)
            else:
                print("\nNo metadata found.")

    def run(self):
        """Execute the full pipeline."""
        chunks = self.load_and_process_pdfs()
        self.create_vector_store(chunks)
        self.access_chroma_objects()

# Run the pipeline
if __name__ == "__main__":
    # Define directories
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    db_dir = os.path.join(os.path.dirname(__file__), "chroma_db")

    pipeline = ChromaDBPipeline(data_dir, db_dir)
    pipeline.run()
