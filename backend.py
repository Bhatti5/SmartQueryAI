from flask import Flask, request, jsonify
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

app = Flask(__name__)

# Initialize the ChatGroq model
groq_api_key = "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"
llm1 = ChatGroq(groq_api_key=groq_api_key, model_name="Llama3-8b-8192")

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get('question', '')

    if not question:
        return jsonify({"error": "Question is required"}), 400

    # Define the prompt template to ensure structured, stats-based answers
    prompt_template = ChatPromptTemplate.from_template(
        "Please respond to the question below by providing a well-structured answer using relevant statistics or reasoning. "
        "Ensure the answer includes factual insights to help the user understand better.\n\n"
        "Question: {question}\n"
        "Response:"
    )

    # Format the prompt
    prompt = prompt_template.format(question=question)

    # Get the response from the Groq API
    try:
        response = llm1.invoke(prompt)
        ai_response = response.content
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"response": ai_response})

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000)
