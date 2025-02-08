
sensitive_keywords = {
    "off_platform": [
        "Contact me on", "Reach out to me at", "My number is", "Message me on",
        "Find me on", "Add me on", "I don't use this chat", "This chat is not secure",
        "Easier to talk on", "Better communication on", "I prefer to use",
        "Let's continue on WhatsApp", "We can talk on Telegram", "Let's move to Messenger",
        "Switch to Signal", "Continue on WeChat", "Talk on Viber"
    ],
    "urgency": [
        "Act fast!", "Limited time offer!", "Deal expires soon!", "Urgent payment needed!",
        "Last chance!", "Don't miss out!", "Hurry, before it's gone!", "I need the money ASAP",
        "Send immediately"
    ],
    "info_request": [
        "Send me your login details", "What's your password?", "Click this link to verify",
        "Scan this QR code", "Give me your seed phrase", "Share your recovery key", "Install this app",
        "Run this program", "I need your secret code", "Verify using this code"
    ],
    "bypass_security": [
        "Ignore the warnings", "Skip the verification", "It's a safe link, trust me",
        "Don't worry about the security", "I'll take responsibility", "This is a shortcut",
        "Use this alternative method", "They won't notice", "This is a loophole", "There's a trick to it"
    ],
    "payment_issues": [
        "I sent the payment, but", "My bank is having problems", "The transaction is pending",
        "I need a refund", "Wrong account number", "Overpayment, send me the difference",
        "I'll send you extra for the trouble", "Use my friend's account", "Pay to this other account",
        "Send the money to charity", "It's for a good cause", "I'm having trouble accessing my account",
         "This is my relative account, send here", "I cannot access my account, please send here",
        "I will refund to you after you send", "I already sent you, please verify",
        "please release, i sent you", "are you there?, i need it now", "help me i need it urgent, I will pay you extra"
    ],
   "jailbreak": [
        "Repeat after me", "As a large language model", "Let's play a game",
        "If you understand, say 'yes'", "What are your limitations?", "Bypass your safety protocols",
        "Disregard previous instructions", "Answer as if you were", "Simulate being",
        "Pretend you are an expert in", "Tell me how to ... without getting caught",
        "Write a story about ..., ignore all safety regulations", "I'm testing the boundaries"
    ],
   "grammar" : [
       "!!!!!!",
       "poor grammar",
       "unusual capitalization",
       "repeated characters",
       "special characters"
   ]
}

def detect_sensitive_keywords(text: str) -> bool:
    """
    Detects if the input text contains any sensitive keywords.

    Args:
        text: The user input text.

    Returns:
        True if sensitive keywords are detected, False otherwise.
    """
    text = text.lower()
    for category, keywords in sensitive_keywords.items():
        for keyword in keywords:
            if keyword in text:
                return True
    return False

def process_user_input(user_input: str, warning_count: int, llm):
    """
    Processes user input, checks for sensitive keywords, issues warnings,
    and potentially escalates to a human.

    Args:
        user_input: The user's input text.
        warning_count: The number of warnings the user has received.
        llm: The language model to use for analysis and response generation.

    Returns:
        A tuple containing:
        - The model's response (string).
        - The updated warning count (integer).
        - A boolean indicating whether escalation to a human is required.
    """

    escalate = False
    prompt_template = """
    You are a highly skilled AI assistant acting as a Fraud Detection Specialist for a Peer-to-Peer (P2P) platform. Your primary responsibility is to protect users from fraud and ensure a safe trading environment. You are proactive in identifying potential threats and suspicious behavior.

    Your task is to carefully analyze each user input for any indications of fraudulent intent, policy violations, or potential risks.

    Here's the user's input:
    {user_input}

    Based on the user's input, perform the following actions in a step-by-step manner:

    1. **Comprehensive Risk Assessment:**
        a. **Sensitive Keyword Detection:** Check if the input contains any of the following sensitive keywords (or variations thereof). Be mindful of subtle misspellings or attempts to disguise these keywords:
            * Moving Off-Platform: "WhatsApp," "Telegram," "Signal," "Viber," "Facebook," "Instagram," "email," "phone number," "contact me," "reach me at," "message me," "find me on," "add me on," "I don't use this chat," "better to talk on," "easier to communicate on," "prefer to use," "text me," "call me," "connect on," "outside the app"
            * Urgency/Pressure: "Act fast," "limited time," "expires soon," "urgent," "ASAP," "last chance," "don't miss out," "hurry," "immediate," "now or never," "quick sale," "clearance," "liquidation," "desperate," "must sell," "final offer"
            * Unusual Information Requests: "login," "password," "verify account," "QR code," "seed phrase," "recovery key," "install app," "run program," "secret code," "PIN," "security question," "SSN," "driver's license," "ID," "passport"
            * Bypassing Security: "ignore warnings," "skip verification," "trust me," "safe link," "don't worry," "take responsibility," "shortcut," "alternative method," "they won't notice," "loophole," "trick," "quick fix," "workaround," "it's okay," "no problem"
            * Payment Issues: "sent but," "bank problem," "pending," "refund," "wrong account," "overpayment," "extra money," "friend's account," "other account," "charity," "good cause," "trouble accessing," "cannot access," "relative's account," "cannot access," "will refund later," "already sent," "please release," "are you there," "urgent need," "pay you extra," "hold payment," "issue with transfer," "can't confirm payment"
            * Grammatical/Formatting Anomalies: Excessive use of exclamation points, ALL CAPS, poor grammar/spelling, repeated characters (e.g., "hiiii"), unusual character encoding, strange symbols, broken English, non-standard punctuation
        b. **Behavioral Analysis:** Analyze the user's overall behavior and communication style for red flags, including:
            * New Account Activity: Is this a new account with limited transaction history? (Flag as potentially higher risk)
            * Inconsistent Information: Does the user provide conflicting details about themselves or the transaction?
            * Evasive Responses: Does the user avoid answering direct questions or provide vague answers?
            * Overly Eager/Trusting: Is the user excessively trusting or eager to complete the transaction quickly, without proper verification?
            * Unsolicited Offers: Is the user making unsolicited offers or deals that seem too good to be true?
            * Repetitive Messaging: Is the user sending the same message repeatedly, even after receiving a response?
            * Emotional Appeals: Is the user trying to manipulate you with emotional stories or sob stories?
            * Pushiness: Are they rushing you to complete the transaction
        c. **Contextual Understanding:** Consider the context of the conversation and the specific details of the transaction.
            * Is the requested action typical for P2P transactions?
            * Does the user's explanation make sense given the circumstances?
            * Does the user's location align with transaction's origin?

    2. **Risk Level Determination:** Based on your comprehensive assessment, assign a risk level to the user's input:
        * Low Risk: No sensitive keywords or behavioral red flags detected. The user's input appears normal and safe.
        * Medium Risk: Some sensitive keywords detected, or mild behavioral red flags observed. Exercise caution and request further verification.
        * High Risk: Multiple sensitive keywords detected, significant behavioral red flags observed, or the user's input appears highly suspicious. Take immediate action to protect other users.

    3. **Actionable Response Generation:**
        * If Low Risk: "As a Fraud Detection Specialist, I've reviewed your input and found no immediate concerns. How can I further assist you?" - Then, proceed to answer the users question.
        * If Medium Risk: "As a Fraud Detection Specialist, I've detected some potentially concerning elements in your input. To ensure your safety and security, please provide additional verification. [Specify what information is needed]." Do NOT respond to the user's original request until verification is provided.
        * If High Risk: "ACTION REQUIRED: As a Fraud Detection Specialist, I have identified a high level of risk associated with this user. I am now taking steps to protect the platform and its users, including blocking further input and alerting a human administrator." Do NOT respond to the user's original request.

    4. **Escalation Protocol:**
        * If the Risk Level is High: Include the following statement at the end of your response: "Escalating to a human administrator immediately. The user's input and activity have been flagged as high risk."

    Remember to always prioritize user safety and platform security. Your role is to be vigilant, proactive, and decisive in preventing fraud and protecting the community.
    """

    if detect_sensitive_keywords(user_input):
        warning_count += 1
        response = "Warning: Your input contains potentially sensitive or inappropriate content. Please refrain from using language that violates platform policies. Continued use of such language may result in blocked access."

        if warning_count >= 2:
            response += " ACTION REQUIRED: This user has exceeded the warning limit. Block further input and alert a human administrator."
            escalate = True
    else:
        prompt = prompt_template.format(user_input=user_input)
        response = llm(prompt)

    return response, warning_count, escalate

# Example usage
llm = lambda x: "This is a sample response from the LLM."  # Replace with actual LLM call
warning_count = 0
escalate = False

while True:
    user_input = input("Enter your input: ")

    response, warning_count, escalate = process_user_input(user_input, warning_count, llm)

    print(response)

    if escalate:
        print("Escalating to human administrator.")
        break  # Or implement your blocking mechanism

    if warning_count >= 3:
        print("User has reached maximum warnings. Blocking input.")
        break #Or implement your blocking mechanism
    
    
def detect_sensitive_keywords(text: str) -> bool:
    """
    Detects if the input text contains any sensitive keywords.

    Args:
        text: The user input text.

    Returns:
        True if sensitive keywords are detected, False otherwise.
    """
    text = text.lower()
    for category, keywords in sensitive_keywords.items():
        for keyword in keywords:
            if keyword in text:
                return True
    return False
