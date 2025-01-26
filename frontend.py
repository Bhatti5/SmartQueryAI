import requests
import streamlit as st

st.title("AI Assistant with Structured Responses")

# Input question
question = st.text_input("Enter your question:")

# Button to trigger AI response
if st.button("Ask AI"):
    if question.strip():
        try:
            # Send POST request to backend
            response = requests.post(
                "http://127.0.0.1:5000/ask",
                json={"question": question}
            )
            # Check for a successful response
            if response.status_code == 200:
                # Extract response content
                ai_response = response.json().get("response", "No response received.")
                st.success(ai_response)
            else:
                st.error(f"Error: Received status code {response.status_code}")
        except Exception as e:
            st.error(f"Failed to connect to backend: {e}")
    else:
        st.warning("Please enter a question before asking.")
