import streamlit as st
import os
from openai import AzureOpenAI
import tiktoken
import re
from typing import List
from dotenv import load_dotenv
load_dotenv()

client = AzureOpenAI(
    # Azure OpenAI Client
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)
# Deployment names
GPT_DEPLOYMENT = "gpt-4o-mini"
EMBED_DEPLOYMENT = "text-embedding-ada-002"

# Tokenizer For Chunking (if still needed for large logs)
tokenizer = tiktoken.get_encoding('cl100k_base')

@st.cache_data
def extract_error_context(log_text: str) -> List[str]:
    """
    Extract triplets: previous, current, and next line for any line containing 'error' (case-insensitive).
    """
    lines = log_text.splitlines()
    error_context = []
    error_pattern = re.compile(r'error', re.IGNORECASE)

    for i, line in enumerate(lines):
        if error_pattern.search(line):
            prev_line = lines[i-1] if i > 0 else ''
            next_line = lines[i+1] if i+1 < len(lines) else ''
            context_snippet = prev_line + '\n' + line + '\n' + next_line
            error_context.append(context_snippet)
    return error_context


def get_embedding(text: str):
    """
    Generate embedding for text.
    """
    response = client.embeddings.create(
        model=EMBED_DEPLOYMENT,
        input=text
    )
    return response.data[0].embedding

def analyze_log(error_context: List[str]):
    """
    Analyze the error context pairs using GPT.
    """
    if not error_context:
        return "No errors detected in log."
    
    context = "\n\n".join(error_context)
    prompt = f"""You are a log analysis expert. Analyze these application log excerpts for errors, issues, or anomalies:

{context}

Identify the exact error(s), root cause, and step-by-step resolution. Be precise, use bullet points for steps, and reference log lines if possible.
"""
    response = client.chat.completions.create(
        model=GPT_DEPLOYMENT,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=1500
    )
    return response.choices[0].message.content

st.title("GenAI Log Analyzer")
st.write("Upload application logs (text/JSON) to detect errors and get resolutions powered by Azure OpenAI.")

uploaded_file = st.file_uploader("Choose log file", type=["txt", "log", "json"])

if uploaded_file:
    log_text = uploaded_file.read().decode("utf-8")
    st.text_area("Raw Log Preview", log_text[:2000], height=200)

    if st.button("Analyze Logs"):
        with st.spinner("Analyzing... Extracting error context and querying LLM."):
            error_lines = extract_error_context(log_text)
            analysis = analyze_log(error_lines)
            st.markdown("### Analysis Results")
            st.markdown(analysis)
