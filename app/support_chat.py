import os
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import RetrievalQA
from dotenv import load_dotenv

load_dotenv()


class LLMWithTools:
    def __init__(self) -> None:
        self.llm = ChatOpenAI(model="gpt-4o")
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        self.parser = StrOutputParser()
        self.persist_directory = os.path.join(os.curdir, './db')
        self.collection_name = "indian_food"
        self.vector_store = Chroma(
            embedding_function=self.embeddings,
            collection_name=self.collection_name,
            persist_directory=self.persist_directory
        )
        self.retriever = self.vector_store.as_retriever(k=3)

    def invoke(self,  messages, input: str,) -> str:
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=self.retriever,
            chain_type='stuff'
        )
        response = qa_chain.invoke(input)
        return response['result'] if 'result' in response else ''
