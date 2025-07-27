from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
load_dotenv()

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vector_store = Chroma(
    embedding_function=embeddings,
    collection_name="indian_food",
    persist_directory="../db"
)
result = vector_store.similarity_search('what is shop name', k=1)
print(result)
