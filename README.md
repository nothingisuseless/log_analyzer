# log_analyzer
Analyzes the log and shares the step by step resolution


## Packages Used

streamlit: Builds the web UI.

os: Reads environment variables.

AzureOpenAI: Azure OpenAI client for GPT & embeddings.

tiktoken: Tokenizer (useful for chunking large logs).

re: Regular expressions for finding errors.

List: Type hinting.

dotenv: Loads secrets from .env.


## Usage:

streamlit run log_analyzer.py
