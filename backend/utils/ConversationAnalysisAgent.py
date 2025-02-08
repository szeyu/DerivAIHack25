import openai
import os
from dotenv import load_dotenv
from typing import Dict

class ConversationAnalysisAgent:
    def __init__(self, model: str = "gpt-4o-mini"):
        load_dotenv()
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key

    def analyze_conversation(self, conversation_chain: str) -> str:
        """
        Analyzes the conversation chain and determines which tool to use.
        :param conversation_chain: The entire conversation chain as a string.
        :return: The name of the selected tool.
        """
        available_tools = {
            "refundBuyer": "The buyer has paid but the seller has not provided the agreed-upon value. A refund is required.",
            "transactionIssues": "There are issues with the transaction itself, such as payment failures or incorrect amounts.",
            "neutralIssue": "No dispute has been identified in the conversation. The issue is neutral or resolved."
        }

        prompt = f"""
        You are an intelligent assistant that analyzes conversations between buyers and sellers.
        Based on the conversation, you will determine which tool to use to resolve the issue.

        Available Tools:
        {available_tools}

        Conversation Chain:
        {conversation_chain}

        Analyze the conversation and return ONLY the name of the most suitable tool.
        """

        response = openai.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a conversation analysis assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        tool_name = response.choices[0].message.content.strip()
        return tool_name

# Example usage:
if __name__ == "__main__":
    agent = ConversationAnalysisAgent()

    # Example conversation chain
    conversation_chain = """
    Buyer: I paid for the product but haven't received it yet.
    Seller: I haven't received the payment confirmation.
    Buyer: Here's the transaction ID: 12345.
    Seller: I see the payment now, but the product is out of stock.
    Buyer: I need a refund then.
    """

    selected_tool = agent.analyze_conversation(conversation_chain)
    print(f"Selected Tool: {selected_tool}")