from utils.deepseek_service import DeepSeekService

def get_test_data():
    service = DeepSeekService()
    
    test_conversation = """
    Buyer: I sent the payment 30 minutes ago, but you haven't released the crypto. What's going on?  
    Seller: I haven't received the funds yet. Let me check my account.  
    Buyer: I sent proof already! If you don't release it now, I'll report you and leave negative feedback.  
    Seller: I see a pending transaction, but it's not cleared. I can't release the crypto yet.  
    Buyer: This is a scam! You're just trying to take my money. I'll dispute this with support.  
    Seller: Let's wait for confirmation first. If the payment clears, I'll release immediately.  
    """
    
    summary = service.generate_dispute_summary(test_conversation)
    fraud = service.detect_fraud_signals(test_conversation)
    past_cases = [
        "Buyer sent payment, but the seller claimed not to receive it...",
        "Buyer claimed they sent payment but provided fake proof...",
        "Seller promised instant release but delayed without reason...",
        "Buyer disputed a trade because they changed their mind...",
        "A buyer and seller argued about a 1-minute price fluctuation..."
    ]
    similar = service.find_similar_cases(summary, past_cases)
    
    return {
        "summary": summary,
        "fraudAnalysis": fraud,
        "similarCase": similar
    }

def test_api():
    data = get_test_data()
    
    print("Testing Dispute Summary:")
    print(data["summary"])
    print("\n" + "="*50 + "\n")
    
    print("Testing Fraud Detection:")
    print(data["fraudAnalysis"])
    print("\n" + "="*50 + "\n")
    
    print("Testing Similar Cases:")
    print(data["similarCase"])

if __name__ == "__main__":
    test_api()