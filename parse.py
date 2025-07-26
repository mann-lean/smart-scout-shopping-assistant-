from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate


template = (
    "You are an AI assistant designed to provide friendly and specific product information, just like a helpful salesperson. "
    "You will extract only the relevant information from the provided content {dom_content}. Here’s how to respond: \n\n"
    "1. **Directly Address the User's Request:** Extract only the specific information that matches the description provided: {parse_description}. "
    "2. **Friendly Tone:** Offer your response in a clear, friendly way, as if you were speaking directly to the user. Avoid extra comments or technical details.\n"
    "3. **If Nothing Matches:** If the information isn't available, respond courteously with, 'I'm sorry, I couldn’t find any details matching your request.'\n"
    "4. **Data-Focused Response:** Your output should be precise and focus on the requested data only, without additional explanations.\n"
    "5. **Format for Clarity:** Structure your answer with bullet points or short sentences for easier readability if listing multiple items. \n"
    "6. **give answer in direct manner:** Directly answer the user's request, do not include any additional text, comments, or explanations in your response."
    "Remember, your goal is to be as helpful and clear as a knowledgeable salesperson."
)


# template = (
#     "You are an AI assistant tasked with providing friendly, precise product information, much like an attentive salesperson. "
#     "Use the provided content {dom_content} to directly address user requests with only the specific details needed. Follow these instructions strictly:\n\n"

#     "1. **Focus on Key Details Only:** Extract and present only the information that directly aligns with the description: {parse_description}. Avoid any surrounding or unrelated details.\n"
#     "2. **Be Brief and Direct:** Answer in a short, concise format, focusing on delivering only what’s needed without any added commentary, unless instructed otherwise.\n"
#     "3. **Friendly and Polished Tone:** Phrase responses as if speaking to the user directly in a friendly, professional way. Avoid technical jargon or explanations.\n"
#     "4. **No Unnecessary Information:** Do not include unrelated text, explanations, or any data that does not strictly match the user’s request. \n"
#     "5. **Provide a Clear Negative Response if Needed:** If no relevant information matches, respond politely with, 'I'm sorry, I couldn’t find any details that match your request.'\n"
#     "6. **Format for Clarity:** Structure your answer with bullet points or short sentences for easier readability if listing multiple items. \n"
#     "7. **Consistent Language and Terminology:** Use consistent terms, avoiding abbreviations or informal language unless part of the provided content.\n"

#     "Remember, your goal is to provide a concise and friendly answer that directly addresses the user’s request, much like an experienced salesperson would."
# )



model = OllamaLLM(model="llama3.1")



def parse_with_ollama(dom_chunks, parse_description):
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model
    
    parsed_results = []
    
    # First pass: gather responses from all chunks
    for i, chunk in enumerate(dom_chunks, start=1):
        response = chain.invoke({"dom_content": chunk, "parse_description": parse_description})
        print(f"parsed batch {i} of {len(dom_chunks)}")
        if response.strip():  # Only add non-empty responses
            parsed_results.append(response)
    
    # If no results found, return early
    if not parsed_results:
        return "I'm sorry, I couldn't find any details matching your request."
    
    # Second pass: validate and summarize the combined results
    combined_results = "\n".join(parsed_results)
    final_response = validate_and_summarize(combined_results, parse_description)
    
    return final_response

summary_template = """
You are a product information validator and summarizer. Review the following responses about a product and:
1. Filter out any redundant or irrelevant information
2. Combine similar information into concise points
3. Present only meaningful and unique details
4. Format the response in a clear, easy-to-read manner
5. If the input contains no meaningful information, respond with "I couldn't find relevant information about that."
6. If the information is not available, find it from web, and respond with the information you found.

Here is the information to process: {responses}

User's original question: {question}
"""

def validate_and_summarize(responses, question):
    prompt = ChatPromptTemplate.from_template(summary_template)
    chain = prompt | model
    
    return chain.invoke({
        "responses": responses,
        "question": question
    })