import openai
import os
from dotenv import load_dotenv
from typing import List, Dict

class ToolsSelectionAgent:
    def __init__(self, model: str = "gpt-4o-mini"):
        load_dotenv()
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key

    def select_tool(self, context: str, available_tools: Dict[str, str]) -> str:
        """
        Given a context, this function determines which tool should be used.
        :param context: The input context to analyze.
        :param available_tools: A dictionary mapping tool names to their descriptions.
        :return: The name of the selected tool.
        """
        prompt = f"""
        You are an intelligent assistant that selects the most appropriate tool based on the given context.
        Below is a list of available tools:
        {available_tools}
        
        Based on the following context, return only the name of the most suitable tool:
        Context: {context}
        """
        
        response = openai.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": "You are a tool selection assistant."},
                      {"role": "user", "content": prompt}],
            temperature=0
        )
        
        tool_name = response.choices[0].message.content.strip()
        return tool_name

# Example usage:
if __name__ == "__main__":
    agent = ToolsSelectionAgent()
    available_tools = {
        "getBuyerBankStatement": "The buyer info is not enough and need to fetch and store the buyer's bank statement as a PDF again.",
        "getSellerBankStatement": "The seller info is not enough and need to fetch and store the seller's bank statement as a PDF again.",
        "notifyAndEscalate": "Automate notifications and escalate cases that require human intervention.",
    }
    context = "The buyer needs to upload their bank statement."
    selected_tool = agent.select_tool(context, available_tools)
    print(selected_tool)
