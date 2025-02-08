from dotenv import load_dotenv
import openai
from typing import Dict
import os
from utils.ToolsSelectionAgent import ToolsSelectionAgent
from utils.OCRScanner import OCRScanner

# -------------------------
# Pipeline Class
# -------------------------
class DisputeResolutionPipeline:
    def __init__(self, model: str = "gpt-4"):
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
            "getBuyerBankStatement": "The buyer info is not enough and need to fetch and store the buyer's bank statement as a PDF again.",
            "getSellerBankStatement": "The seller info is not enough and need to fetch and store the seller's bank statement as a PDF again.",
            "notifyAndEscalate": "Automate notifications and escalate cases that require human intervention.",
        }

    def resolve_dispute(self, conversation_chain: str, proof_1: str, proof_2: str) -> str:
        """
        Resolves a P2P dispute by analyzing proofs of transaction.

        Args:
            conversation_chain: All the input of the conversation between the two sides.
            proof_1: The text content from OCR analysis of Proof of Transaction 1.
            proof_2: The text content from OCR analysis of Proof of Transaction 2.

        Returns:
            A string containing the resolution, or an escalation message.
        """
        prompt_template = """
You are an Experienced Payment Fraud Analyst. You investigate suspicious transactions and chargebacks for a Peer-to-Peer (P2P) platform. Your goal is to efficiently resolve disputes by validating proofs of transfer and identifying fraudulent activity.

Here's the information you have:

* Conversation Chain between User 1 and User 2:
{conversation_chain}

* Proof of Transfer (User 1):
{proof_1}

* Proof of Transfer (User 2):
{proof_2}

Follow these steps to analyze the situation and determine a fair resolution:

1. Initial Assessment:
    a. Based on the conversation, identify the dispute category if possible (e.g., "Buyer not paid", "Seller not released items", "Buyer underpaid", "Buyer overpaid").
    b. Specify what information is most vital in each of the proofs based on the identified dispute category.

2. Proof Validation:
    a. Validity Check: Assess the validity of each proof individually. Consider factors such as:
        * Presence of expected fields (transaction ID, dates, amounts, sender/recipient information).
        * Internal consistency (e.g., amounts matching the claimed transfer).
        * Overall coherence and readability (limited OCR errors).
        * Authenticity: Check for signs of tampering or forgery (e.g., inconsistent fonts, watermarks, unusual formatting).
    b. Comparison: Compare the two proofs, focusing on:
        * Transaction details (dates, amounts, IDs).
        * Parties involved (sender/recipient).
        * Any other relevant information.
        * Consistency: Verify that the information on both proofs aligns with the claimed transaction details.

3. Resolution Determination: Based on your analysis, determine the appropriate resolution:

    a. **Scenario A**: Both proofs are valid, and all details match the dispute category.
        * If 'Buyer not paid': "The proof provided by User 2 (seller) is validated. Releasing funds to the buyer, User 1."
        * If 'Seller not released items': "The proof provided by User 1 (buyer) is validated. Releasing funds to the seller (releasing the items), User 2."
        * If 'Buyer underpaid': "Underpayment confirmed. The buyer, User 1, needs to pay the remaining amount."
        * If 'Buyer overpaid': "Overpayment confirmed. The buyer, User 1, will receive a refund."
        * **Escalation Trigger**: Include the following statement at the end of your response: "Confirmed transaction and took action automatically. No human assistance needed."

    b. **Scenario B**: Both proofs are valid and in the correct format, but some details conflict.
        * Resolution: "There are conflicting details between the two proofs provided by User 1 and User 2. Further review is required and needs human intervention."
        * **Escalation Trigger**: Include the following statement at the end of your response: "Escalating to a human administrator due to conflicting details."

    c. **Scenario C**: Only one proof is valid and in the correct format.
        * Resolution: Explain which proof is considered valid and why. Investigate the other proof for potential fraud. Recommend steps for the party with the invalid proof.
        * **Escalation Trigger**: Include the following statement at the end of your response: "Escalating to a human administrator due to invalid documents."

    d. **Scenario D**: One or more pieces of information are missing.
        * Resolution: State what information is missing. Request that the user provide the missing requirements.
        * **Escalation Trigger**: Include the following statement at the end of your response: "Escalating to a human administrator due to missing requirements."

    e. **Scenario E**: Evidence of fraud or forgery detected in one or both proofs.
        * Resolution: "Evidence of fraud/forgery detected in [specify which document]. Taking immediate action to protect the platform and its users. Freezing funds and accounts related to this transaction."
        * **Escalation Trigger**: Include the following statement at the end of your response: "Escalating to a human administrator due to suspected fraud/forgery."

4. Fraud Monitoring:
    * Throughout your analysis, be vigilant for signs of fraud, including:
        * Altered dates, times, or amounts.
        * Inconsistent fonts or watermarks.
        * Mismatched sender/recipient information.
        * Unusual formatting or language.
        * Any other suspicious anomalies.

Generate a concise resolution based on your analysis, including specific actions taken and explanations.

Action Taken and Resolution:
"""
        prompt = prompt_template.format(
            conversation_chain=conversation_chain,
            proof_1=proof_1,
            proof_2=proof_2
        )

        # Call the LLM to generate the resolution
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an experienced payment fraud analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        resolution = response.choices[0].message['content'].strip()
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
    pipeline = DisputeResolutionPipeline(model="gpt-4")

    # Define the conversation chain and PDF file paths
    conversation_chain = """
User 1: I sent the payment yesterday, but I haven't received the items yet.
User 2: I haven't received any payment from you. Please check your bank.
User 1: Here's my bank statement showing the transfer.
User 2: That's strange; I don't see it on my end.
"""

    pdf_file1 = "/path/to/proof1.pdf"  # Replace with actual path for Proof of Transaction 1 (User 1)
    pdf_file2 = "/path/to/proof2.pdf"  # Replace with actual path for Proof of Transaction 2 (User 2)

    # Process the dispute
    result = pipeline.process_dispute(conversation_chain, pdf_file1, pdf_file2)

    # Display the output
    print("Dispute Resolution:")
    print(result["resolution"])
    print("\nSelected Tool:")
    print(result["selected_tool"])