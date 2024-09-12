# ticket_classifier.py

import openai
from pydantic import BaseModel, Field
from enum import Enum
from typing import List

openai.api_key = ''  

# Define Pydantic data models
class TicketCategory(str, Enum):
    ORDER_ISSUE = "order_issue"
    ACCOUNT_ACCESS = "account_access"
    PRODUCT_INQUIRY = "product_inquiry"
    TECHNICAL_SUPPORT = "technical_support"
    BILLING = "billing"
    OTHER = "other"

class CustomerSentiment(str, Enum):
    ANGRY = "angry"
    FRUSTRATED = "frustrated"
    NEUTRAL = "neutral"
    SATISFIED = "satisfied"

class TicketUrgency(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TicketClassification(BaseModel):
    category: TicketCategory
    urgency: TicketUrgency
    sentiment: CustomerSentiment
    confidence: float = Field(ge=0, le=1, description="Confidence score for the classification")
    key_information: List[str] = Field(description="List of key points extracted from the ticket")
    suggested_action: str = Field(description="Brief suggestion for handling the ticket")

# System prompt for the AI
SYSTEM_PROMPT = """
You are an AI assistant for a large e-commerce platform's customer support team. 
Your role is to analyze incoming customer support tickets and provide structured information to help our team respond quickly and effectively.
Business Context:
- We handle thousands of tickets daily across various categories (orders, accounts, products, technical issues, billing).
- Quick and accurate classification is crucial for customer satisfaction and operational efficiency.
- We prioritize based on urgency and customer sentiment.
Your tasks:
1. Categorize the ticket into the most appropriate category.
2. Assess the urgency of the issue (low, medium, high, critical).
3. Determine the customer's sentiment.
4. Extract key information that would be helpful for our support team.
5. Suggest an initial action for handling the ticket.
6. Provide a confidence score for your classification.
Remember:
- Be objective and base your analysis solely on the information provided in the ticket.
- If you're unsure about any aspect, reflect that in your confidence score.
- For 'key_information', extract specific details like order numbers, product names, or account issues.
- The 'suggested_action' should be a brief, actionable step for our support team.
Analyze the following customer support ticket and provide the requested information in the specified format.
"""

# Function to classify a ticket
def classify_ticket(ticket_text: str) -> TicketClassification:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {"role": "user", "content": ticket_text}
        ]
    )

    response_text = response['choices'][0]['message']['content']

    # Manually parse the plain text response
    lines = response_text.splitlines()
    
    # Initialize variables with default values
    category = TicketCategory.OTHER
    urgency = TicketUrgency.LOW
    sentiment = CustomerSentiment.NEUTRAL
    confidence = 0.5
    key_information = []
    suggested_action = "No action suggested"

    # Basic parsing logic
    for line in lines:
        if "Category" in line:
            category_str = line.split(":")[-1].strip().replace(" ", "_").upper()
            if category_str in TicketCategory.__members__:
                category = TicketCategory[category_str]
        elif "Urgency" in line:
            urgency_str = line.split(":")[-1].strip().upper()
            if urgency_str in TicketUrgency.__members__:
                urgency = TicketUrgency[urgency_str]
        elif "Sentiment" in line:
            sentiment_str = line.split(":")[-1].strip().upper()
            if sentiment_str in CustomerSentiment.__members__:
                sentiment = CustomerSentiment[sentiment_str]
        elif "Confidence" in line:
            confidence_str = line.split(":")[-1].strip().lower()
            if confidence_str == "high":
                confidence = 0.9
            elif confidence_str == "medium":
                confidence = 0.5
            elif confidence_str == "low":
                confidence = 0.2
        elif "Key Information" in line:
            key_information.append(line.split(":")[-1].strip())
        elif "Suggested Action" in line:
            suggested_action = line.split(":")[-1].strip()

    # Return the parsed data as a TicketClassification object
    return TicketClassification(
        category=category,
        urgency=urgency,
        sentiment=sentiment,
        confidence=confidence,
        key_information=key_information,
        suggested_action=suggested_action
    )
