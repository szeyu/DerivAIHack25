def resolve_dispute(dispute_category: str, proof_1: str, proof_2: str, llm):
    """
    Resolves a P2P dispute by analyzing proofs of transaction.

    Args:
        dispute_category: The category of the dispute (e.g., "Buyer not paid").
        proof_1: The text content from OCR analysis of Proof of Transaction 1.
        proof_2: The text content from OCR analysis of Proof of Transaction 2.
        llm: The language model to use for analysis and response generation.

    Returns:
        A string containing the resolution, or an escalation message.
    """

    prompt_template = """
    You are a Experienced Payment Fraud Analyst. You investigate suspicious transactions and chargebacks for a Peer-to-Peer (P2P) platform. Your goal is to efficiently resolve disputes by validating proofs of transfer and identifying fraudulent activity.

    Here's the information you have:

    * Dispute Category: {dispute_category}
    * Proof of Transfer (User 1): {proof_1}
    * Proof of Transfer (User 2): {proof_2}

    Follow these steps to analyze the situation and determine a fair resolution:

    1. Initial Assessment:
        a. Determine if the provided proofs of transfer are in the correct format (video or PDF). If not, request the user to provide the correct format. Photos are NOT accepted.
        b. Based on the dispute category, specify what information is most vital in each of the proofs.
            *   **Buyer not paid:** The validity of the user 2 is more crucial here.
            *   **Seller not released items:** The validity of the user 1 is more crucial here.
            *   **Buyer underpaid:** both proofs need to be cross-checked here
            *   **Buyer overpaid:** both proofs need to be cross-checked here

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

        a. Scenario A: Both proofs are valid, in the correct format (video or PDF), and all details match the dispute category.
            * If 'Buyer not paid': "The proof provided by seller(User 2) is validated. Releasing funds to the buyer, User 1."
            * If 'Seller not released items': "The proof provided by buyer(User 1) is validated. Releasing funds to the Seller (releasing the items), User 2."
            * If 'Buyer underpaid': "Underpayment confirmed, the buyer, User 1, needs to pay the remaining amount."
            * If 'Buyer overpaid': "Overpayment confirmed, the user, User 2 will get refund"
            * Escalation Trigger: Include the following statement at the end of your response: "Confirmed Transaction and took action automatically. No human assistance needed."

        b. Scenario B: Both proofs are valid and in the correct format, but some details conflict.
            * Resolution: "There are conflicting details between the two proofs, User 1 and User 2. Further Review may be required and need human intervention."
            * Escalation Trigger: Include the following statement at the end of your response: "Escalating to a human administrator, Conflicting Details"

        c. Scenario C: Only one proof is valid and in the correct format.
            * Resolution: Explain which proof is considered valid and why. Investigate the other proof for potential fraud. Recommend steps for the party with the invalid proof.
            * Escalation Trigger: Include the following statement at the end of your response: "Escalating to a human administrator, Invalid Documents"

        d. Scenario D: One or both proofs are not in the correct format (not video or PDF).
            * Resolution: Explain what is wrong. Request that the user provide evidence with the correct format and valid documents again.
            * Escalation Trigger: Include the following statement at the end of your response: "Escalating to a human administrator, Correct format Required"

        e. Scenario E: One or more information is missing.
            * Resolution: State what are those information. Request that the user provide again those requirements.
            * Escalation Trigger: Include the following statement at the end of your response: "Escalating to a human administrator, Requirement Missing"

        f. Scenario F: There is evidence of fraud or forgery detected in one or both proofs.
            * Resolution: "Evidence of fraud/forgery detected in [specify which document]. Taking immediate action to protect the platform and its users. Freezing funds and accounts related to this transaction"
            * Escalation Trigger: Include the following statement at the end of your response: "Escalating to a human administrator, Fraud / Forgery"

    4. Fraud Monitoring:
        * Throughout your analysis, be vigilant for signs of fraud, including:
            * Altered dates, times, or amounts
            * Inconsistent fonts or watermarks
            * Mismatched sender/recipient information
            * Unusual formatting or language
            * Any other suspicious anomalies

    Generate a concise resolution based on your analysis, including specific actions taken and explanations.

    Action Taken and Resolution:
    """

    prompt = prompt_template.format(
        dispute_category=dispute_category,
        proof_1=proof_1,
        proof_2=proof_2
    )

    resolution = llm(prompt)
    return resolution

def escalate_to_human(resolution: str) -> bool:
    """Determines if the resolution needs a human."""
    return "escalating to a human administrator" in resolution.lower()

# Example usage
llm = lambda x: "This is a sample response from the LLM, no errors"  # Replace with your actual LLM call

dispute_category = "Buyer not paid"
proof_1_text = "Example Proof of Transfer (Buyer): [Details]"
proof_2_text = "Example Proof of Transfer (Seller): [Details]"

resolution = resolve_dispute(dispute_category, proof_1_text, proof_2_text, llm)

print(f"Dispute Resolution:\n{resolution}")

if escalate_to_human(resolution):
    print("Human intervention is required.")
else:
    print("AI successfully resolved the dispute automatically.")
