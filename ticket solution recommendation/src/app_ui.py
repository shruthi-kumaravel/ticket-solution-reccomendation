# app.py

import streamlit as st
import pandas as pd
from ticket_classifier import classify_ticket

st.title("Customer Care Ticket Classifier")

# Input box for entering a customer care ticket
ticket_text = st.text_area("Enter your customer care ticket here:")

if st.button("Classify Ticket"):
    if ticket_text:
        # Classify the ticket
        classification = classify_ticket(ticket_text)
        
        # Display the classification results
        st.subheader("Classification Results")
        st.write(f"**Category:** {classification.category}")
        st.write(f"**Urgency:** {classification.urgency}")
        st.write(f"**Sentiment:** {classification.sentiment}")
        st.write(f"**Confidence:** {classification.confidence}")
        st.write(f"**Key Information:** {', '.join(classification.key_information)}")
        st.write(f"**Suggested Action:** {classification.suggested_action}")

        # Save to CSV option
        if st.button("Save to CSV"):
            results_df = pd.DataFrame([{
                'review_text': ticket_text,
                'category': classification.category,
                'urgency': classification.urgency,
                'sentiment': classification.sentiment,
                'confidence': classification.confidence,
                'key_information': classification.key_information,
                'suggested_action': classification.suggested_action
            }])
            results_df.to_csv('classified_ticket.csv', index=False)
            st.success("Results saved to classified_ticket.csv")
    else:
        st.error("Please enter a customer care ticket.")
