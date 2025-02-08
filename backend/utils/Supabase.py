import supabase
from dotenv import load_dotenv
import os

load_dotenv()

class DatabaseChecker:
    def __init__(self, url: str, key: str):
        """Initialize the Supabase client."""
        self.client = supabase.create_client(url, key)

    def is_blacklisted(self, username: str) -> bool:
        """
        Check if the given username is blacklisted.
        
        :param username: The name of the user to check.
        :return: True if the user is blacklisted, False otherwise.
        """
        response = self.client.table("users").select("blacklist").eq("name", username).execute()
        
        # Check if user exists
        if response.data and len(response.data) > 0:
            return response.data[0]['blacklist']  # Return True if user is blacklisted
        return False  # User not found or no blacklist info

# Example usage
if __name__ == "__main__":
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    user_checker = DatabaseChecker(url, key)
    
    username = "Alice"
    if user_checker.is_blacklisted(username):
        print(f"{username} is blacklisted!")
    else:
        print(f"{username} is not blacklisted.")
