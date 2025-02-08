from dotenv import load_dotenv
import openai
from typing import Dict
import os
from .ToolsSelectionAgent import ToolsSelectionAgent
from .OCRScanner import OCRScanner

# -------------------------
# Pipeline Class
# -------------------------
class DisputeResolutionPipeline:
    def __init__(self, model: str = "gpt-4o"):
        """
        Initializes the dispute resolution pipeline with:
         - An LLM callable for dispute resolution.
         - A ToolsSelectionAgent for selecting follow-up tools.
         - An OCRScanner to convert PDF proofs to Markdown.
         - A dictionary of available tools.
        """
        # Load environment variables and set up OpenAI API
        load_dotenv()
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key

        # Initialize other components
        self.tools_agent = ToolsSelectionAgent(model=model)
        self.ocr_scanner = OCRScanner()
        self.available_tools = {
            "getBuyerBankStatement": "The buyer does not upload a valid bank statement and the buyer info is not enough and need to fetch and store the buyer's bank statement as a PDF again.",
            "getSellerBankStatement": "The buyer does not upload a valid bank statement and the seller info is not enough and need to fetch and store the seller's bank statement as a PDF again.",
            "notifyAndEscalate": "Automate notifications and escalate cases that require human intervention.",
            "allGood": "Both parties are all good and the transaction is completed successfully.",
        }

    def resolve_dispute(self, conversation_chain: str, proof_buyer: str, proof_seller: str) -> str:
        """
        Resolves a P2P dispute by analyzing proofs of transaction and determines if an additional action (via a tool) is needed.

        Args:
            conversation_chain: All the input of the conversation between the two sides.
            proof_buyer: The text content from OCR analysis of the Buyer's proof of transaction.
            proof_seller: The text content from OCR analysis of the Seller's proof of transaction.

        Returns:
            A string containing a concise resolution in two sentences and a tool selection line.
        """

        prompt_template = """
    You are an Experienced Payment Fraud Analyst investigating suspicious transactions for a Peer-to-Peer (P2P) platform. Your goal is to efficiently resolve disputes by validating proofs of transfer and identifying fraudulent activity.

    Here's the information you have:

    * Conversation Chain between Buyer and Seller:
    {conversation_chain}

    * Proof of Transfer (Buyer):
    {proof_buyer}

    * Proof of Transfer (Seller):
    {proof_seller}

    Follow these steps to analyze the situation and determine a fair resolution:

    1. **Initial Assessment:**
        - Identify the dispute category (e.g., "Buyer not paid", "Seller not released items", "Buyer underpaid", "Buyer overpaid") based on the conversation.
        - Highlight which pieces of information are most vital in each proof.

    2. **Proof Validation:**
        - **Validity Check:** Evaluate each proof for:
            * Presence of expected fields (transaction ID, dates, amounts, sender/recipient information).
            * Internal consistency (e.g., matching amounts).
            * Coherence and readability (limited OCR errors).
            * Signs of tampering or forgery (e.g., inconsistent fonts, watermarks, unusual formatting).
        - **Comparison:** Compare both proofs regarding:
            * Transaction details (dates, amounts, IDs).
            * Parties involved.
            * Overall consistency between the proofs.

    3. **Resolution Determination and Tool Selection:**
        Based on your analysis, decide on the resolution and select an appropriate tool from the following:

        - **getBuyerBankStatement:** Use this if the Buyer's provided document is invalid or insufficient and the buyer's bank statement must be fetched as a PDF again.
        - **getSellerBankStatement:** Use this if the Seller's provided document is invalid or insufficient and the seller's bank statement must be fetched as a PDF again.
        - **notifyAndEscalate:** Use this if conflicting details that require human intervention.
        - **allGood:** Use this if both proofs are valid and consistent, and the transaction is completed successfully.

    4. **Output Requirements:**
        - Summarize your analysis and resolution in **two sentences**.
        - End your response with a new line that specifies the selected tool in the exact format:
        selected_tool: <tool>
        where `<tool>` is one of: getBuyerBankStatement, getSellerBankStatement, notifyAndEscalate, or allGood.

    5. **Fraud Monitoring:**
        - Be alert to any signs of fraud, such as altered dates/times/amounts, mismatched sender/recipient info, inconsistent formatting, or any other suspicious anomalies.

    Action Taken and Resolution:
        """

        prompt = prompt_template.format(
            conversation_chain=conversation_chain,
            proof_buyer=proof_buyer,
            proof_seller=proof_seller
        )

        # Call the LLM to generate the resolution
        response = openai.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an experienced payment fraud analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        resolution = response.choices[0].message.content.strip()
        return resolution

    def process_dispute(self, conversation_chain: str, pdf_file1: str, pdf_file2: str) -> Dict[str, str]:
        """
        Processes the dispute end-to-end:
         1. Uses OCRScanner to convert the two PDF proofs into Markdown.
         2. Calls the LLM to resolve the dispute based on the conversation chain and OCR results.
         3. Determines whether human intervention is needed.
         4. Uses the ToolsSelectionAgent to select the most appropriate follow-up tool based on the dispute resolution context.

        Returns:
            A dictionary containing:
              - "resolution": The dispute resolution string generated by the LLM.
              - "selected_tool": The tool selected by the ToolsSelectionAgent.
        """
        # Convert PDF proofs to Markdown text using OCR
        proof_1 = self.ocr_scanner.convert_pdf_to_markdown(pdf_file1)
        proof_2 = self.ocr_scanner.convert_pdf_to_markdown(pdf_file2)

        # Generate dispute resolution via the LLM
        resolution = self.resolve_dispute(conversation_chain, proof_1, proof_2)

        # Use resolution as context for tool selection
        selected_tool = self.tools_agent.select_tool(resolution, self.available_tools)

        return {
            "resolution": resolution,
            "selected_tool": selected_tool
        }

# -------------------------
# Example usage of the pipeline
# -------------------------
if __name__ == "__main__":
    # Instantiate the pipeline
    pipeline = DisputeResolutionPipeline(model="gpt-4o")

    # Define the conversation chain and PDF file paths
    conversation_chain = """
User 1: I sent the payment yesterday, but I haven't received the items yet.
User 2: I haven't received any payment from you. Please check your bank.
User 1: Here's my bank statement showing the transfer.
User 2: That's strange; I don't see it on my end.
"""

    pdf_file1 = "/home/ssyok/Documents/Hackathons/DerivAIHack25/backend/data/GXBank Transaction buyer fake.pdf"  # Replace with actual path for Proof of Transaction 1 (User 1)
    pdf_file2 = "/home/ssyok/Documents/Hackathons/DerivAIHack25/backend/data/GXBank Transaction seller.pdf"  # Replace with actual path for Proof of Transaction 2 (User 2)

    # Process the dispute
    result = pipeline.process_dispute(conversation_chain, pdf_file1, pdf_file2)

    # Display the output
    print("Dispute Resolution:")
    print(result["resolution"])
    print("\nSelected Tool:")
    print(result["selected_tool"])