# OpenAI Whisper speech to text
from openai import OpenAI
client = OpenAI(api_key=OPENAI_WHISPER_API_KEYS)

audio_file= open("/path/to/file/audio.mp3", "rb")
transcription = client.audio.transcriptions.create(
    model="whisper-1", 
    file=audio_file
)

print(transcription.text)


# text to audio
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play

load_dotenv()

client = ElevenLabs()

audio = client.text_to_speech.convert(
    text="The first move is what sets everything in motion.",
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_multilingual_v2",
    output_format="mp3_44100_128",
)

play(audio)


# image to text Vision Language Model

import requests, base64

invoke_url = "https://ai.api.nvidia.com/v1/gr/meta/llama-3.2-90b-vision-instruct/chat/completions"
stream = True

with open("image.png", "rb") as f:
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
  "temperature": 1.00,
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



import os
import chromadb
from chromadb.utils import embedding_functions
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from sentence_transformers import SentenceTransformer  # Ensure this is installed


def extract_relevant_chunks(embedding, vectordb, n_results=20):
    """
    Retrieves relevant chunks from ChromaDB based on the input embedding.

    Args:
        embedding (list): The embedding vector for the query.
        vectordb (Chroma): The Chroma vector store.
        n_results (int): Number of results to retrieve.

    Returns:
        list: A list of retrieved documents.
    """
    results = vectordb.similarity_search_by_vector(embedding=embedding, k=n_results)
    return results


def resolve_dispute(user_text, openai_api_key, vectordb, collection_name, embedding_model):
    """
    Orchestrates the dispute resolution process.

    Args:
        user_text (str): The user's input text.
        openai_api_key (str): OpenAI API key.
        vectordb (Chroma):  The Chroma vector store.
        collection_name (str): The name of the collection (not really used now).
        embedding_model:  SentenceTransformer model
    Returns:
        str: A dispute resolution report.
    """
    # Assume these functions are defined elsewhere (as stubs for this example):
    def user_input(text):  return text
    def speech_to_text(a, b): return ""
    def image_to_text(a, b, c): return ""
    def create_embedding(text, model): return model.encode(text).tolist()  # Use SentenceTransformer directly
    def prepare_input(user_text, relevant_chunks): return user_text + "\n" + "\n".join(relevant_chunks)
    def analyze_dispute(combined_input, openai_api_key): return "Analyzed: " + combined_input
    def generate_report(analysis_result): return "Report: " + analysis_result


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
    relevant_chunks = extract_relevant_chunks(embedding, vectordb, n_results=3) #Pass vectordb, not client
    combined_input = prepare_input(user_text, relevant_chunks)

    # Reasoning Stage
    analysis_result = analyze_dispute(combined_input, openai_api_key)

    # Final Response to User
    report = generate_report(analysis_result)
    return report


# ----------------------- Example Usage -----------------------
if __name__ == "__main__":
    # 1.  Configure ChromaDB to run locally
    db_dir = os.path.join(os.path.dirname(__file__), "chroma_db") #Local directory
    #Initialize embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2",
        model_kwargs={'device': 'cpu'}
    )

    #Check Chroma Instance locally.
    vectordb = Chroma(persist_directory=db_dir, embedding_function=embeddings)

    #2.  Sample data for ChromaDB (replace with your actual data)
    collection_name = "dispute_resolution_knowledge"

    #Check if the vectordb is empty
    if len(vectordb.get()['ids']) == 0:
        print("Adding data to ChromaDB...")
        documents=[
            "According to contract law, both parties must fulfill their obligations as stated in the contract.",
            "Past cases have shown that failure to deliver goods on time can result in financial penalties.",
            "Mediation is often a successful first step in resolving business disputes."
        ]
        ids=["doc1", "doc2", "doc3"]
        vectordb.add_texts(documents=documents, ids=ids)

    # 3. Initialize Sentence Transformer model  (move initialization here)
    embedding_model = SentenceTransformer('all-mpnet-base-v2') #Moved here

    # 4. Get OpenAI API key from environment variables
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

    # 5. Sample user input
    user_text = "I ordered goods from a supplier, but they were delivered a week late, causing me financial losses. The supplier claims the delay was due to unforeseen circumstances."

    # 6. Resolve the dispute
    report = resolve_dispute(user_text, openai_api_key, vectordb, collection_name, embedding_model) # Pass vectordb, not client.
    print(report)