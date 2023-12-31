import streamlit as st
from llama_index import VectorStoreIndex, ServiceContext, Document
from llama_index.llms import OpenAI
import openai
from llama_index import SimpleDirectoryReader

# Update this line to the correct path to your data folder
reader = SimpleDirectoryReader(input_dir="/home/gia86326/VisualStudioProjects/Luc/.streamlit/data", recursive=True)

openai.api_key = st.secrets.openai_key
st.header("Chat with Luc")

if "messages" not in st.session_state.keys():  # Initialize the chat message history
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question about what you wrote"}
    ]
st.write(f"API Key Start: {st.secrets.openai_key[:4]}... End: {st.secrets.openai_key[-4:]}")





@st.cache_resource(show_spinner=False)
def load_data():
    try:
        with st.spinner(
            text="Loading and indexing the Streamlit docs – hang tight! This should take 1-2 minutes."
        ):
            reader = SimpleDirectoryReader(input_dir="/home/gia86326/VisualStudioProjects/Luc/.streamlit/data", recursive=True)
            docs = reader.load_data()
            service_context = ServiceContext.from_defaults(
                llm=OpenAI(
                    model="gpt-3.5-turbo",
                    temperature=0.5,
                    system_prompt="You are an expert on the Streamlit Python library and your job is to answer technical questions. Assume that all questions are related to the Streamlit Python library. Keep your answers technical and based on facts – do not hallucinate features.",
                )
            )
            index = VectorStoreIndex.from_documents(docs, service_context=service_context)
            return index
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None



index = load_data()

chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

if prompt := st.chat_input("Your question"):  # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages:  # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = chat_engine.chat(prompt)
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message)  # Add response to message history



