import streamlit as st 
import time
# from amazon import scrape_website
from amazon import scrape_website, split_dom_content, clean_body_content, extract_body_content, remove_unwanted_sections
from parse import parse_with_ollama


# Add this near the top where other session state initializations are
if "show_input" not in st.session_state:
    st.session_state.show_input = True

# Replace the URL input section with this conditional block
if st.session_state.show_input:
    col1, col2 = st.columns([6,1], gap="small")
    with col1:
        url = st.text_input("", placeholder="Enter a product URL", label_visibility="collapsed")
    with col2:
        if st.button('Go', use_container_width=True):
            with st.spinner("Scraping the website.."):
                html_content = scrape_website(url)
                # Process the HTML content
                body_content = extract_body_content(html_content)
                cleaned_content = clean_body_content(body_content)
                filtered_content = remove_unwanted_sections(body_content)
                final_cleaned_content = clean_body_content(filtered_content)
                
                st.session_state.dom_content = final_cleaned_content
                # Hide the input after successful scraping
                st.session_state.show_input = False

# Initialize chat history in session state if not present
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Update the animated_text function
def animated_text(placeholder, text, duration=0.5):
    """Creates an animated thinking effect"""
    dots = ["", ".", "..", "..."]
    start_time = time.time()
    while time.time() - start_time < duration:
        for dot in dots:
            placeholder.markdown(f"🤔 **THINKING{dot}**")
            time.sleep(0.2)

# Modify the chat input section
if prompt := st.chat_input("What would you like to know about this product?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.write(prompt)
    
    with st.chat_message("assistant"):
        if "dom_content" in st.session_state:
            message_placeholder = st.empty()
            
            dom_chunks = split_dom_content(st.session_state.dom_content)
            total_chunks = len(dom_chunks)
            
            try:
                # Process chunks and update status
                processed_chunks = []
                print("\n 🔍 Querying Ollama...")
                for i, chunk in enumerate(dom_chunks, 1):
                    message_placeholder.write(f"Parsed batch {i} of {total_chunks}")
                    processed_chunks.append(chunk)
                
                animated_text(message_placeholder, "THINKING")
                
                response = parse_with_ollama(processed_chunks, prompt)
                message_placeholder.write(response)
                
                # Add to history after successful response
                st.session_state.messages.append({"role": "assistant", "content": response})
                print("\n ✅ Query completed")
            except ConnectionError:
                message_placeholder.write("Error: Unable to connect to Ollama. Please make sure Ollama is running and try again.")
            except Exception as e:
                message_placeholder.write(f"An error occurred: {str(e)}")
        else:
            st.write("Please enter a product URL first and click Go to scrape the website.")


# reset the chat history
if st.button("Reset"):
    st.session_state.messages = []
    st.session_state.show_input = True  # Show the input again
    if "dom_content" in st.session_state:
        del st.session_state.dom_content

