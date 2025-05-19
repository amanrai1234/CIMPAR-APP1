# cimpar_inventory_chat.py

import openai
import streamlit as st
import pandas as pd
import os
from openai import OpenAI
from dotenv import load_dotenv

# Set Streamlit page config
st.set_page_config(page_title="CIMPAR Inventory Assistant", layout="wide")

# Load API key from secrets.toml
api_key = st.secrets["OPENAI"]["api_key"]

if not api_key:
    st.error("❌ OpenAI API key not found.")
    st.stop()

# Initialize OpenAI client
openai.api_key = api_key

# Load and flatten Excel data
@st.cache_resource
def load_inventory(file_path: str) -> str:
    try:
        sheets = pd.read_excel(file_path, sheet_name=None)
        sheet_texts = []
        for name, df in sheets.items():
            text = f"Sheet: {name}\n{df.to_string(index=False)}"
            sheet_texts.append(text)
        return "\n\n".join(sheet_texts)
    except Exception as e:
        st.error(f"❌ Failed to load Excel file: {e}")
        return ""

# Path to inventory Excel file
file_path = "inventroy.xlsx"
all_data = load_inventory(file_path)

# --- UI HEADER ---
st.image("cimpar_logo.png", width=150)
st.markdown("<h1 style='text-align: left; margin-bottom: 0;'>🔷 CIMPAR Inventory Assistant</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='margin-top: 0;'>Ask any question about your inventory Excel file.</h4>", unsafe_allow_html=True)
st.info("This AI assistant reads your Excel inventory and answers questions with full row context.")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User query input
query = st.chat_input("Ask about the inventory...")

# Display chat history
for role, content in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(content)

# Process query
if query:
    st.session_state.chat_history.append(("user", query))
    with st.chat_message("user"):
        st.markdown(query)

    with st.spinner("Thinking..."):
        try:
            response = openai.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": (
                        "You are an IT assistant. Use the provided inventory data to answer questions. "
                        "The inventory data is messy and badly labeled. If I ask about tablets or any items, "
                        "retrieve everything relevant — show full rows and explain what you inferred from them. "
                        "Answer with full Excel-format rows to impress users. Include context and a clear explanation."
                    )},
                    {"role": "user", "content": f"Inventory Data:\n{all_data}"},
                    *[
                        {"role": role, "content": content}
                        for role, content in st.session_state.chat_history
                        if role == "user"
                    ],
                    {"role": "user", "content": query}
                ]
            )
            answer = response.choices[0].message.content  # ✅ Corrected here
        except Exception as e:
            answer = f"❌ OpenAI API call failed: {e}"

        st.session_state.chat_history.append(("assistant", answer))
        with st.chat_message("assistant"):
            st.markdown(answer)
