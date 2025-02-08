import openai
from sentence_transformers import SentenceTransformer
import chromadb
import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play
from elevenlabs import VoiceSettings
from openai import OpenAI
import requests, base64
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()

def user_input(text_input):
    """
    Acquires user input text.
    In a real application, this would be a more complex data ingestion pipeline.
    """
    return text_input

def create_embedding(text, model):
    """
    Generates an embedding for the given text using Sentence Transformers.
    """
    embedding = model.encode(text)
    return embedding

def extract_relevant_chunks(embedding, chromadb_client, collection_name, n_results=20):
    """
    Retrieves relevant chunks from ChromaDB based on the input embedding.
    """
    collection = chromadb_client.get_collection(collection_name)
    results = collection.query(
        query_embeddings=[embedding],
        n_results=n_results
    )
    return results['documents']

def prepare_input(user_text, relevant_chunks):
    """
    Combines user input text and extracted chunks for the reasoning stage.
    """
    combined_input = f"Dispute context: {user_text}\n\nRelevant knowledge:\n"
    combined_input = " -" + "\n\n -".join(relevant_chunks)
    return combined_input

def speech_to_text(audio_file_path, openai_api_key, model="whisper-1"):
    """
    Transcribes speech to text using OpenAI Whisper.
    """
    # OpenAI Whisper speech to text
    client = OpenAI(api_key=openai_api_key)

    audio_file= open("audio_file_path", "rb")
    transcription = client.audio.transcriptions.create(
        model=model, 
        file=audio_file
    )

    print(transcription.text)
    
def text_to_speech(model_output_text, voice_id, model_id, output_format):
        # text to audio

    client = ElevenLabs(api_key=os.environ.get("ELEVENLABS_API_KEY"))

    audio = client.text_to_speech.convert(
        text=model_output_text,
        voice_id="NpVSXJvYSdIbjOaMbShj",
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
        voice_settings=VoiceSettings(
            stability=0.3,
            similarity_boost=0.0,
            style=0.5,
            use_speaker_boost=True,
        )
    )

    play(audio)
    
def image_to_text(image_path, invoke_url, api_key):

    invoke_url = "https://ai.api.nvidia.com/v1/gr/meta/llama-3.2-90b-vision-instruct/chat/completions"
    stream = False

    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode()

    assert len(image_b64) < 180_000, \
    "To upload larger images, use the assets API (see docs)"
    

    headers = {
    "Authorization": "Bearer $API_KEY_REQUIRED_IF_EXECUTING_OUTSIDE_NGC",
    "Accept": "text/event-stream" if stream else "application/json"
    }

    payload = {
    "model": 'meta/llama-3.2-90b-vision-instruct',
    "messages": [
        {
        "role": "user",
        "content": f'What is in this image? <img src="data:image/png;base64,{image_b64}" />'
        }
    ],
    "max_tokens": 512,
    "temperature": 0.00,
    "top_p": 1.00,
    "stream": stream
    }

    response = requests.post(invoke_url, headers=headers, json=payload)

    if stream:
        for line in response.iter_lines():
            if line:
                print(line.decode("utf-8"))
    else:
        print(response.json())



# ----------------------- Reasoning Stage -----------------------

def analyze_dispute(combined_input, openai_api_key, model="gpt-3.5-turbo-16k", previous_messages=[]):
    """
    Analyzes the dispute and generates a potential resolution using OpenAI.
    """
    openai.api_key = openai_api_key  #Replace with your actual API key
    if len(previous_messages) > 0:
        prompt = f"""
        You are a dispute resolution expert. You will be given a dispute scenario explained by the user, along with relevant rules and regulations / terms and conditions about the dispute.
        The dispute information provided by the end user will include ordinary chat texts, description of images, and/or OCR content extracted from the images the end user provided.
        Your task is to analyze the information provided and propose a resolution to the dispute. You should consider the context, rules, and any other relevant information to come up with a fair and reasonable resolution.
        
        # STEPS:
        1. Analyze the scenario based on the dispute infromation provided.
        2. Look for relevant rules and regulations / terms and conditions about the dispute.
        3. Formulate a resolution that is fair and reasonable based on the information provided. 
        4. Your output must be very simple, short and concise. You may include minimal justification or reasoning if required. You must adopt a patient and helpful Malaysian tone in your output. You may include malaysian slangs or phrases like "lah", "eh", "loh" if necessary to enhance the tone and overall user experience.
        
        Below are your inputs:
        #########################
        {combined_input}
        
        #########################
        
        Your output:
        """
    else:
        prompt = f"""
        You are a dispute resolution expert. You will be given a dispute scenario explained by the user, along with relevant rules and regulations / terms and conditions about the dispute.
        The dispute information provided by the end user will include ordinary chat texts, description of images, and/or OCR content extracted from the images the end user provided.
        Your task is to analyze the information provided and propose a resolution to the dispute. You should consider the context, rules, and any other relevant information to come up with a fair and reasonable resolution.
        
        # STEPS:
        1. Analyze the scenario based on the dispute infromation provided.
        2. Look for relevant rules and regulations / terms and conditions about the dispute.
        3. Formulate a resolution that is fair and reasonable based on the information provided. 
        4. Your output must be very simple, short and concise. You may include minimal justification or reasoning if required. You must adopt a patient and helpful Malaysian tone in your output. You may include malaysian slangs or phrases like "lah", "eh", "loh" if necessary to enhance the tone and overall user experience.
        
        Below are your inputs:
        #########################
        {previous_messages}
        
        #########################
        
        Your output:
        """
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt},
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error during OpenAI API call: {e}"

# ----------------------- Final Response to User -----------------------

def generate_report(analysis_result):
    """
    Generates a structured dispute resolution report.
    """
    report = f"""
    **Dispute Resolution Report**

    {analysis_result}

    ---
    If you require further clarification or wish to escalate this dispute to a human moderator, please submit your request.
    """
    return report

# ----------------------- Main Function -----------------------

def extract_relevant_chunks(embedding, chromadb_client, collection_name, n_results=20):
    """
    Retrieves relevant chunks from ChromaDB based on the input embedding.
    """
    collection = chromadb_client.get_collection(collection_name)
    results = collection.query(
        query_embeddings=[embedding],
        n_results=n_results
    )
    return results['documents']

def load_and_process_pdfs(data_dir: str):
    """Load PDFs from directory and split into chunks."""
    loader = DirectoryLoader(
        data_dir,
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
    return chunks

def resolve_dispute(user_text, openai_api_key, chromadb_client, collection_name, embedding_model):
    """
    Orchestrates the dispute resolution process.
    """
    # User Input Stage
    user_text = user_input(user_text)
    text = \
    f"""
    User Input: 
    #####################
    {user_text + speech_to_text("", openai_api_key)}
    
    Image Description or Content: 
    #####################
    # {image_to_text("", "", "")}
    """
    embedding = create_embedding(text, embedding_model)
    relevant_chunks = extract_relevant_chunks(embedding, chromadb_client, collection_name)
    combined_input = prepare_input(user_text, relevant_chunks)

    # Reasoning Stage
    analysis_result = analyze_dispute(combined_input, openai_api_key)

    # Final Response to User
    report = generate_report(analysis_result)
    return report

# ----------------------- Example Usage -----------------------
if __name__ == "__main__":
    # Initialize ChromaDB client
    chroma_client = chromadb.HttpClient(host="localhost", port=8000)  # Replace with your ChromaDB connection details
    
    # Initialize vector store and embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2",
        model_kwargs={'device': 'cpu'}
    )
    db_dir = os.path.join(os.path.dirname(__file__), "chroma_db")
    vectordb = Chroma(persist_directory=db_dir, embedding_function=embeddings)

    # Sample data for ChromaDB (replace with your actual data)
    collection_name = "dispute_resolution_knowledge"
    try:
      chroma_client.delete_collection(name=collection_name)
    except:
      pass
    knowledge_collection = chroma_client.create_collection(name=collection_name)
    knowledge_collection.add(
        documents=[
            "According to contract law, both parties must fulfill their obligations as stated in the contract.",
            "Past cases have shown that failure to deliver goods on time can result in financial penalties.",
            "Mediation is often a successful first step in resolving business disputes."
        ], 
    )

    # Initialize Sentence Transformer model
    embedding_model = SentenceTransformer('all-mpnet-base-v2')

    # Get OpenAI API key from environment variables
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

    # Sample user input
    user_text = "I ordered goods from a supplier, but they were delivered a week late, causing me financial losses. The supplier claims the delay was due to unforeseen circumstances."

    # Resolve the dispute
    report = resolve_dispute(user_text, openai_api_key, chroma_client, collection_name, embedding_model)
    print(report)
    
    

import os
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

def create_and_use_chromadb(documents, embeddings_model_name="all-mpnet-base-v2", persist_directory="chroma_db", query=""):
    """
    Creates or loads a ChromaDB, adds documents to it, and performs a similarity search.

    Args:
        documents (list): A list of documents (e.g., from PDF loading).
        embeddings_model_name (str): Name of the HuggingFace embeddings model.
        persist_directory (str): Directory to store the ChromaDB.
        query (str): The search query to perform.

    Returns:
        list: A list of retrieved documents based on the query.
    """

    # 1. Initialize embeddings
    embeddings_model = HuggingFaceEmbeddings(model_name=embeddings_model_name)

    # 2. Load or create ChromaDB
    if os.path.exists(persist_directory):
        # Load existing ChromaDB
        vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings_model)
        print("Loaded existing ChromaDB from disk")
    else:
        # Create new ChromaDB
        vectordb = Chroma.from_documents(documents=documents, embedding=embeddings_model, persist_directory=persist_directory)
        print("Created new ChromaDB from documents")
    vectordb.persist()

    # 3. Perform similarity search if a query is provided
    if query:
        results = vectordb.similarity_search(query, k=10) # You can adjust 'k'
        return results
    else:
        print("No query provided. Returning an empty list.")
        return []