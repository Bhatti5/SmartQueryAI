from flask import Flask, request, jsonify
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from tavily import TavilyClient  # Correct import

app = Flask(__name__)

# Initialize API keys
groq_api_key = "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"
tavily_api_key = "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"

# Initialize AI models
llm1 = ChatGroq(groq_api_key=groq_api_key, model_name="Llama3-8b-8192")  # Answer model
llm2 = ChatGroq(groq_api_key=groq_api_key, model_name="Llama3-8b-8192")  # Evaluation model

# Initialize Tavily API
tavily = TavilyClient(api_key=tavily_api_key)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get('question', '')

    if not question:
        return jsonify({"error": "Question is required"}), 400

    # === Step 1: Generate AI Response ===
    prompt_template = ChatPromptTemplate.from_template(
        "Answer the following question by providing multiple concise statements. "
        "Each statement must follow this exact format:\n\n"
        "[Key point]: [Statistic] ([Source, Year]).\n\n"
        "Ensure:\n"
        "- The response consists of multiple facts.\n"
        "- Each fact includes a percentage, number, or study reference.\n"
        "- No general statements—every line must contain data.\n"
        "- Responses are formatted as separate lines for readability.\n\n"
        "Question: {question}\n"
        "Response:"
    )
    prompt = prompt_template.format(question=question)

    try:
        response = llm1.invoke(prompt)
        ai_response = response.content.strip()
    except Exception as e:
        return jsonify({"error": f"AI Response Failed: {str(e)}"}), 500

    # === Step 2: Fetch References from Tavily ===
    try:
        tavily_response = tavily.search(query=question, num_results=3)  # API call
        print("Tavily Response:", tavily_response)  # Debugging line

        references = [
            {"title": result.get("title", "No Title"), "url": result.get("url", "No URL")}
            for result in tavily_response.get("results", [])
        ]

    except Exception as e:
        references = [{"error": f"Failed to fetch references: {str(e)}"}]

    # === Step 3: Evaluate AI Response ===
    eval_prompt_template = ChatPromptTemplate.from_template(
        "Evaluate the following response based on accuracy, completeness, and formatting. "
        "Provide feedback with a score (1-10) for each category:\n\n"
        "- Accuracy: [Score] - [Justification]\n"
        "- Completeness: [Score] - [Justification]\n"
        "- Formatting: [Score] - [Justification]\n\n"
        "Response:\n{response}\n\n"
        "Evaluation:"
    )
    eval_prompt = eval_prompt_template.format(response=ai_response)

    try:
        eval_response = llm2.invoke(eval_prompt)
        evaluation = eval_response.content.strip()
    except Exception as e:
        evaluation = f"Evaluation failed: {str(e)}"

    # === Step 4: Return JSON Response ===
    return jsonify({
        "response": ai_response,
        "evaluation": evaluation,
        "references": references
    })

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)
