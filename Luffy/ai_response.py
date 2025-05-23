from google.generativeai import GenerativeModel, configure

# Configure Gemini API with your API key (set this once in the project)
# You can alternatively set this in main.py and import your configured model here.
configure(api_key="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")
gemini = GenerativeModel("gemini-pro")

def get_gemini_response(question):
    """
    Sends a question to Gemini AI and returns the generated response text.
    
    Parameters:
        question (str): The user's question.
        
    Returns:
        str: The AI-generated response, or an error message.
    """
    try:
        response = gemini.generate_content(question)
        if hasattr(response, 'text') and response.text:
            return response.text
        else:
            return "I'm sorry, I couldn't generate a response."
    except Exception as e:
        return f"Error generating response: {e}"

# For testing purposes
if __name__ == "__main__":
    sample_question = "What is the capital of France?"
    answer = get_gemini_response(sample_question)
    print("Gemini AI Response:", answer)
