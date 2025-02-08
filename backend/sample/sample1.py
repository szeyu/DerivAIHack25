import os
import re
import time
from typing import List, Dict, Any

# Install necessary libraries (if not already installed)
# os.system("pip install chromadb unstructured pdfminer.six sentence-transformers nltk requests")

import chromadb
from chromadb.utils import embedding_functions
from unstructured.partition.auto import partition
import nltk
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer
import requests
import json

# Download nltk punkt for sentence tokenization
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

# --------------------------------------------------
# 1. User Input & Preprocessing Stage
# --------------------------------------------------

class DataExtractor:
    """
    Extracts and preprocesses dispute-related data from various sources.
    """

    def __init__(self):
        pass

    def extract_structured_data(self, data: Dict) -> Dict:
        """
        Extracts structured data (e.g., transaction details, timestamps) from user input.
        This is a placeholder; implement actual extraction based on your data structure.
        """
        # Replace this with your actual structured data extraction logic
        transaction_details = data.get("transaction_details", {})
        timestamps = data.get("timestamps", [])
        return {"transaction_details": transaction_details, "timestamps": timestamps}

    def pdf_to_semantic_chunks(self, pdf_path: str) -> List[str]:
        """
        Converts unstructured PDF data into semantic chunks using unstructured.
        """
        try:
            elements = partition(filename=pdf_path)
            text = "\n".join([str(el.text) for el in elements])
            sentences = sent_tokenize(text)  # Split into sentences
            # Group sentences into chunks (e.g., 3-5 sentences per chunk)
            chunk_size = 4
            chunks = [" ".join(sentences[i:i + chunk_size]) for i in range(0, len(sentences), chunk_size)]
            return chunks
        except Exception as e:
            print(f"Error processing PDF: {e}")
            return []

    def preprocess_data(self, data: Dict, pdf_files: List[str] = None) -> List[str]:
        """
        Orchestrates the data extraction and preprocessing steps.
        """
        structured_data = self.extract_structured_data(data)
        text_chunks = []

        if pdf_files:
            for pdf_file in pdf_files:
                chunks = self.pdf_to_semantic_chunks(pdf_file)
                text_chunks.extend(chunks)

        # Add structured data as a single chunk
        text_chunks.append(json.dumps(structured_data))
        return text_chunks

# --------------------------------------------------
# 2. Knowledge Retrieval Stage (LLM-1: Retrieval Agent)
# --------------------------------------------------

class KnowledgeRetriever:
    """
    Retrieves relevant knowledge from the vector database using hybrid search.
    """

    def __init__(self, collection_name: str = "dispute_resolution_kb", embedding_model_name: str = 'all-mpnet-base-v2'):
        """
        Initializes the KnowledgeRetriever with ChromaDB client and embedding function.
        """
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path="./chroma_db")  # Store ChromaDB locally
        self.collection_name = collection_name

        # Initialize embedding function
        self.embedding_model = SentenceTransformer(embedding_model_name)

        # Create collection if it doesn't exist
        if self.collection_name not in self.client.list_collections():
            self.collection = self.client.create_collection(
                name=self.collection_name,
            )
        else:
            self.collection = self.client.get_collection(name=self.collection_name)

    def hybrid_search(self, query: str, vector_weight: float = 0.7, keyword_results: int = 2, n_results: int = 5) -> List[str]:
        """
        Performs hybrid search using vector similarity and keyword matching.
        """
        # Vector search
        query_embedding = self.embedding_model.encode(query).tolist()
        vector_results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
        )

        # Keyword search (simple implementation using regex)
        keywords = re.findall(r'\b\w+\b', query.lower())  # Extract words
        keyword_results_list = []
        if keywords:
            all_chunks = self.collection.get(include=["documents"])["documents"]
            if all_chunks:
                keyword_results_list = [
                    chunk for chunk in all_chunks if any(keyword in chunk.lower() for keyword in keywords)
                ]

        # Combine and rank results (simple weighted approach)
        combined_results = {}
        for i, doc in enumerate(vector_results["documents"][0]): # vector_results is a dict, access the documents list inside
            if doc:
                combined_results[doc] = combined_results.get(doc, 0) + vector_weight * (n_results - i)

        for doc in keyword_results_list[:keyword_results]:
            combined_results[doc] = combined_results.get(doc, 0) + (1 - vector_weight) * n_results

        ranked_results = sorted(combined_results.items(), key=lambda item: item[1], reverse=True)
        return [doc for doc, score in ranked_results]

    def adaptive_retrieval(self, query: str, initial_n_results: int = 3, confidence_threshold: float = 0.8, max_iterations: int = 3) -> List[str]:
        """
        Dynamically retrieves more chunks if confidence is low, up to a maximum number of iterations.
        """
        retrieved_chunks = self.hybrid_search(query, n_results=initial_n_results)
        # Placeholder for confidence calculation (replace with actual LLM call)
        confidence = self.estimate_confidence(query, retrieved_chunks)

        iteration = 1
        while confidence < confidence_threshold and iteration < max_iterations:
            initial_n_results *= 2  # Double the number of results
            retrieved_chunks = self.hybrid_search(query, n_results=initial_n_results)
            confidence = self.estimate_confidence(query, retrieved_chunks)
            iteration += 1

        return retrieved_chunks

    def estimate_confidence(self, query: str, context: List[str]) -> float:
        """
        Placeholder for estimating confidence using an LLM.
        This should be replaced with an actual LLM call to assess the relevance
        and completeness of the retrieved context for answering the query.
        """
        # In a real implementation, you would use an LLM to evaluate the
        # relevance and completeness of the context.
        # This is a placeholder that returns a random confidence score.
        # confidence_score = random.random()
        # print(f"Estimated confidence: {confidence_score}")
        # return confidence_score

        # A Simple Example using LLM-3 (Judge Agent)
        judge_prompt = f"""
        You are a judge agent. Assess the quality of the context to answer the query.
        Query: {query}
        Context: {context}
        Give a confidence score between 0 and 1. If the context is relevant and sufficient to answer the query, give a high score. If the context is irrelevant or insufficient, give a low score.
        Return a json object with a "confidence" key and a float value.
        """

        response = self.call_llm(judge_prompt, model="Judge")
        try:
            json_response = json.loads(response)
            confidence_score = float(json_response.get("confidence", 0.0))
            print(f"Estimated confidence: {confidence_score}")
            return confidence_score
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error decoding JSON or accessing 'confidence': {e}")
            return 0.0


    def early_stopping_retrieval(self, query: str, confidence_threshold: float = 0.95, n_results: int = 5) -> List[str]:
        """
        Retrieves chunks and stops early if a high-confidence answer is found.
        """
        retrieved_chunks = self.hybrid_search(query, n_results=n_results)
        confidence = self.estimate_confidence(query, retrieved_chunks)

        if confidence >= confidence_threshold:
            print("Early stopping triggered: High-confidence answer found.")
            return retrieved_chunks
        else:
            return retrieved_chunks

    def retrieve_knowledge(self, query: str, adaptive: bool = True, early_stopping: bool = False) -> List[str]:
        """
        Main function to retrieve knowledge, using adaptive retrieval or early stopping if enabled.
        """
        if early_stopping:
            return self.early_stopping_retrieval(query)
        elif adaptive:
            return self.adaptive_retrieval(query)
        else:
            return self.hybrid_search(query)

    def call_llm(self, prompt: str, model: str = "Retrieval") -> str:
        """
        Calls a Large Language Model (LLM) to generate responses.
        Replace with your actual LLM API endpoint and authentication.
        """
        # Define the API endpoint based on the model type
        if model == "Retrieval":
            api_url = os.environ.get("LLM_1_API_URL")  # Replace with your LLM-1 Retrieval Agent API endpoint
        elif model == "Resolution":
            api_url = os.environ.get("LLM_2_API_URL")  # Replace with your LLM-2 Dispute Resolution Agent API endpoint
        elif model == "Judge":
            api_url = os.environ.get("LLM_3_API_URL")  # Replace with your LLM-3 Judge Agent API endpoint
        else:
            raise ValueError("Invalid model type. Choose 'Retrieval', 'Resolution', or 'Judge'.")

        headers = {
            "Content-Type": "application/json",
            "Authorization": os.environ.get("LLM_API_KEY"),  # Replace with your API key or authentication method
        }

        data = {"prompt": prompt}
        try:
            response = requests.post(api_url, headers=headers, data=json.dumps(data), timeout=60)  # Adjust timeout as needed
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()["response"]  # Assuming the response is a JSON with a "response" key
        except requests.exceptions.RequestException as e:
            print(f"Error calling LLM API: {e}")
            return ""

    def add_data_to_db(self, documents: List[str], metadatas: List[Dict[str, Any]] = None, ids: List[str] = None):
        """
        Adds data to the ChromaDB collection.
        """
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )

# --------------------------------------------------
# 3. Primary Reasoning Stage (LLM-2: Dispute Resolution Agent)
# --------------------------------------------------

class DisputeResolver:
    """
    Analyzes the dispute context and retrieved knowledge to propose resolutions.
    """

    def __init__(self, knowledge_retriever: KnowledgeRetriever):
        self.knowledge_retriever = knowledge_retriever

    def initial_analysis(self, dispute_context: str) -> str:
        """
        Identifies core issues and conflict points in the dispute context.
        """
        prompt = f"""
        Analyze the following dispute context and identify the core issues and conflict points:
        {dispute_context}
        Provide a summary of the main points of contention.
        """
        return self.knowledge_retriever.call_llm(prompt, model="Resolution")

    def solution_generation(self, dispute_context: str, retrieved_knowledge: List[str]) -> str:
        """
        Proposes potential resolutions based on retrieved knowledge.
        """
        knowledge_string = "\n".join(retrieved_knowledge)
        prompt = f"""
        Based on the following dispute context and retrieved knowledge, propose potential resolutions:
        Dispute Context: {dispute_context}
        Retrieved Knowledge: {knowledge_string}
        Provide a detailed explanation of each proposed resolution, including the reasoning behind it.
        """
        return self.knowledge_retriever.call_llm(prompt, model="Resolution")

    def self_verification(self, initial_solution: str, dispute_context: str, retrieved_knowledge: List[str]) -> str:
        """
        Checks for contradictions or missing knowledge in the initial solution.
        """
        knowledge_string = "\n".join(retrieved_knowledge)
        prompt = f"""
        You are in self verification stage, check the initial solution for contradictions or missing knowledge based on the dispute context and retrieved knowledge. If found, please fix it.
        Dispute Context: {dispute_context}
        Retrieved Knowledge: {knowledge_string}
        Initial Solution: {initial_solution}
        Provide a revised solution, include reasons for the revision.
        """
        return self.knowledge_retriever.call_llm(prompt, model="Resolution")

    def resolve_dispute(self, dispute_context: str) -> str:
        """
        Main function to resolve the dispute, orchestrating the reasoning process.
        """
        analysis = self.initial_analysis(dispute_context)
        retrieved_knowledge = self.knowledge_retriever.retrieve_knowledge(dispute_context)
        solution = self.solution_generation(dispute_context, retrieved_knowledge)
        verified_solution = self.self_verification(solution, dispute_context, retrieved_knowledge)
        return verified_solution

# --------------------------------------------------
# 4. Adjudication & Quality Control (LLM-3: Judge Agent)
# --------------------------------------------------

class JudgeAgent:
    """
    Evaluates the coherence, fairness, and completeness of the proposed resolution.
    """

    def __init__(self, knowledge_retriever: KnowledgeRetriever):
        self.knowledge_retriever = knowledge_retriever

    def evaluate_solution(self, dispute_context: str, proposed_solution: str) -> Dict[str, Any]:
        """
        Evaluates the coherence, fairness, and completeness of the proposed solution.
        """
        prompt = f"""
        Evaluate the following proposed solution for a dispute, considering its coherence, fairness, and completeness:
        Dispute Context: {dispute_context}
        Proposed Solution: {proposed_solution}
        Provide a confidence score (0-1) indicating your certainty in the quality of the solution.
        Also, provide a brief justification for your score, highlighting any strengths or weaknesses of the solution.
        Return a json object with "confidence" key (float value between 0 and 1) and "justification" key (string).
        """
        response = self.knowledge_retriever.call_llm(prompt, model="Judge")
        try:
            json_response = json.loads(response)
            confidence = float(json_response.get("confidence", 0.0))
            justification = json_response.get("justification", "")
            return {"confidence": confidence, "justification": justification}
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error decoding JSON or accessing 'confidence' and 'justification': {e}")
            return {"confidence": 0.0, "justification": "Failed to evaluate solution."}

    def refine_solution(self, dispute_context: str, proposed_solution: str) -> str:
        """
        Asks the Dispute Resolver to refine the response if confidence is low.
        """
        prompt = f"""
        The following proposed solution for a dispute has been deemed insufficient. Refine the solution to improve its coherence, fairness, and completeness:
        Dispute Context: {dispute_context}
        Proposed Solution: {proposed_solution}
        Provide a revised solution that addresses the identified weaknesses.
        """
        return self.knowledge_retriever.call_llm(prompt, model="Resolution")

    def select_best_solution(self, dispute_context: str, solutions: List[str]) -> str:
        """
        Selects the best solution from multiple generated solutions.
        """
        evaluations = [self.evaluate_solution(dispute_context, solution) for solution in solutions]
        best_solution = max(zip(solutions, evaluations), key=lambda x: x[1]["confidence"])[0]
        return best_solution

    def adjudicate(self, dispute_context: str, initial_solution: str, confidence_threshold: float = 0.7) -> str:
        """
        Main function to adjudicate the dispute resolution, controlling the quality control loop.
        """
        evaluation = self.evaluate_solution(dispute_context, initial_solution)
        if evaluation["confidence"] > confidence_threshold:
            print("Solution passed quality control.")
            return initial_solution
        else:
            print("Solution failed quality control. Refining response...")
            refined_solution = self.refine_solution(dispute_context, initial_solution)
            evaluation = self.evaluate_solution(dispute_context, refined_solution)  # Evaluate the refined solution

            if evaluation["confidence"] > confidence_threshold:
                print("Refined solution passed quality control.")
                return refined_solution
            else:
                 print("Refined solution also failed quality control. Returning initial solution (may require human review).")
                 return initial_solution

# --------------------------------------------------
# 5. Final Response to User
# --------------------------------------------------

class ReportGenerator:
    """
    Generates a structured dispute resolution report.
    """

    def generate_report(self, dispute_context: str, resolution: str, evaluation: Dict[str, Any] = None) -> str:
        """
        Generates a structured dispute resolution report.
        """
        report = f"""
        Dispute Resolution Report
        --------------------------
        Dispute Context: {dispute_context}

        Key Findings: (Summary of the key issues and conflict points)
        (This section would summarize the findings from the initial analysis)

        Proposed Resolution: {resolution}

        Justification for Resolution: (Explanation of why this resolution is recommended)
        (This section would provide a detailed justification based on retrieved knowledge and reasoning)

        References: (Links to legal documents or past cases used in the analysis)
        (This section would list the relevant references)

        """
        if evaluation:
            report += f"""
        Quality Control Assessment:
        Confidence Score: {evaluation["confidence"]}
        Justification: {evaluation["justification"]}
            """

        report += """
        Additional Clarification:
        If you require further clarification or have any questions, please contact us.
        """
        return report

# --------------------------------------------------
# Main Function & Example Usage
# --------------------------------------------------

def main():
    """
    Main function to orchestrate the dispute resolution process.
    """
    # 1. User Input Stage
    user_data = {
        "dispute_context": "The buyer claims the received product is damaged and demands a full refund. The seller insists the product was in perfect condition when shipped.",
        "transaction_details": {"order_id": "12345", "product_name": "Deluxe Widget", "amount": 100},
        "timestamps": ["2024-10-26T10:00:00Z", "2024-10-27T14:30:00Z"],
    }
    pdf_files = []  # List of paths to PDF files

    data_extractor = DataExtractor()
    text_chunks = data_extractor.preprocess_data(user_data, pdf_files)

    # 2. Knowledge Retrieval Stage
    knowledge_retriever = KnowledgeRetriever()

    # Add initial knowledge base to ChromaDB (example)
    initial_knowledge = [
        "According to our policy, damaged products are eligible for a full refund if reported within 7 days of receipt.",
        "Sellers are responsible for ensuring products are properly packaged to prevent damage during shipping.",
        "Past cases with similar issues were resolved by offering a 50% refund.",
        "The Consumer Rights Act 2015 states that goods must be of satisfactory quality, fit for purpose and as described."
    ]

    # Add Ids for the documents in the knowledge base
    knowledge_ids = ["doc1", "doc2", "doc3", "doc4"]

    knowledge_retriever.add_data_to_db(documents=initial_knowledge, ids = knowledge_ids) # Add the knowledge ids


    # 3. Primary Reasoning Stage
    dispute_resolver = DisputeResolver(knowledge_retriever)
    initial_solution = dispute_resolver.resolve_dispute(user_data["dispute_context"])

    # 4. Adjudication & Quality Control
    judge_agent = JudgeAgent(knowledge_retriever)
    final_resolution = judge_agent.adjudicate(user_data["dispute_context"], initial_solution)

    # 5. Final Response to User
    report_generator = ReportGenerator()
    evaluation = judge_agent.evaluate_solution(user_data["dispute_context"], final_resolution)
    report = report_generator.generate_report(user_data["dispute_context"], final_resolution, evaluation)

    print(report)

if __name__ == "__main__":
    main()