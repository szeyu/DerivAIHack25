from utils.deepseek_service import DeepSeekService

def test_api():
    service = DeepSeekService()
    
    # Sample conversation for testing
    test_conversation = """
    Buyer: Hi, I ordered a smartphone two weeks ago, but I still haven’t received it. The tracking number shows "in transit" with no updates. 

    Seller: Hello, our estimated delivery time is 10-15 business days. Sometimes, there are delays with the courier. Please be patient.

    Buyer: This is ridiculous! You promised fast shipping, and now it’s taking forever. If I don’t get it in 2 days, I will file a chargeback.

    Seller: Sir, I never promised "fast shipping." The listing clearly states the expected timeframe.

    Buyer: That’s not what I remember! I demand a full refund right now, or I’ll report you for fraud.

    Seller: I understand your frustration, but I can only issue a refund if the item is confirmed lost. I will check with the courier.

    Buyer: No! Just give me my money back, or I’ll leave bad reviews everywhere.

    Seller: Let me verify the issue with the shipping company first. I’ll get back to you soon.

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
        "Delivery dispute resolved with partial refund due to delay",
        "Customer complained about 3-week delivery time, resolved with explanation"
    ]
    similar = service.find_similar_cases(summary, past_cases)
    print(similar)

if __name__ == "__main__":
    test_api()