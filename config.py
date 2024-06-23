from dotenv import load_dotenv
import os

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
pinecone_key = os.getenv('PINECONE_API_KEY')
pinecone_env = os.getenv('PINECONE_ENVIRONMENT')
pinecone_index_name = os.getenv('PINECONE_INDEX_NAME')
huggingface_hub_api = os.getenv('HUGGINGFACEHUB_API_TOKEN')

models_used = {"gpt": "gpt-3.5-turbo", "llama": "llama-2-7b-chat.ggmlv3.q4_1.bin"}
