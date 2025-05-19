#cimpar_inventory_chat.py
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
from openai import OpenAI
import os

# Set Streamlit page config
st.set_page_config(page_title="CIMPAR Inventory Assistant", layout="wide")

# Init OpenAI client
# Load environment variables from .env
load_dotenv()

# Get the key securely
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)


# Load Excel data once and flatten
@st.cache_resource
def load_inventory(file_path: str) -> str:
    sheets = pd.read_excel(file_path, sheet_name=None)
    sheet_texts = []
    for name, df in sheets.items():
        text = f"Sheet: {name}\n{df.to_string(index=False)}"
        sheet_texts.append(text)
    return "\n\n".join(sheet_texts)

# Load inventory data
file_path = "inventroy.xlsx"
all_data = load_inventory(file_path)

# --- UI HEADER ---
st.image("cimpar_logo.png", width=150)
st.markdown("<h1 style='text-align: left; margin-bottom: 0;'>🔷 CIMPAR Inventory Assistant</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='margin-top: 0;'>Ask any question about your inventory Excel file.</h4>", unsafe_allow_html=True)
st.info("This AI assistant reads your Excel inventory and answers questions with full row context.")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User input
query = st.chat_input("Ask about the inventory...")

# Display past chat
for role, content in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(content)

# On user submit
if query:
    st.session_state.chat_history.append(("user", query))
    with st.chat_message("user"):
        st.markdown(query)

    with st.spinner("Thinking..."):
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are an IT assistant. Use the provided inventory data to answer questions. The inventory data is messy and badly labeled. If I ask about lets say tablets or some kind of random things, retrieve the relevant information(Retrieve everything related to query- The users care about the answers(FULL EXCEL ROW AND ALSO THE FORMATING) and ESPECIALLY THE WAY THE ANSWER IS PRESENTED!  and explain what it is) explain what you inferred from the data. Also, the above data is from excel so make sure you give the FULL ROW ANSWERS -IMPORTANT! in the excel format to amaze the users haha"},
                {"role": "user", "content": f"Inventory Data:\n{all_data}"},
                *[
                    {"role": role, "content": content}
                    for role, content in st.session_state.chat_history
                    if role == "user"
                ],
                {"role": "user", "content": query}
            ]
        )
        answer = response.choices[0].message.content
        st.session_state.chat_history.append(("assistant", answer))
        with st.chat_message("assistant"):
            st.markdown(answer)
