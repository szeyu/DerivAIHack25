from utils.deepseek_service import DeepSeekService

def test_api():
    service = DeepSeekService()
    
    # Sample conversation for testing
    test_conversation = """
    Buyer: I sent the payment 30 minutes ago, but you haven’t released the crypto. What’s going on?  

    Seller: I haven’t received the funds yet. Let me check my account.  

    Buyer: I sent proof already! If you don’t release it now, I’ll report you and leave negative feedback.  

    Seller: I see a pending transaction, but it’s not cleared. I can’t release the crypto yet.  

    Buyer: This is a scam! You’re just trying to take my money. I’ll dispute this with support.  

    Seller: Let’s wait for confirmation first. If the payment clears, I’ll release immediately.  

    """
    
    print("Testing Dispute Summary:")
    summary = service.generate_dispute_summary(test_conversation)
    print(summary)
    print("\n" + "="*50 + "\n")
    
    print("Testing Fraud Detection:")
    fraud = service.detect_fraud_signals(test_conversation)
    print(fraud)
    print("\n" + "="*50 + "\n")
    
    print("Testing Similar Cases:")
    past_cases = [
        "Buyer sent payment, but the seller claimed not to receive it. After investigation, funds were delayed due to bank processing. Crypto was released after confirmation.",
        "Buyer claimed they sent payment but provided fake proof. Seller reported fraud, and admin ruled in seller’s favor.",
        "Seller promised instant release but delayed without reason. Buyer opened a dispute, and the admin forced release.",
        "Buyer disputed a trade because they changed their mind after payment. Admin rejected the refund request.",
        "A buyer and seller argued about a 1-minute price fluctuation in a volatile market."
    ]
    similar = service.find_similar_cases(summary, past_cases)
    print(similar)

if __name__ == "__main__":
    test_api()