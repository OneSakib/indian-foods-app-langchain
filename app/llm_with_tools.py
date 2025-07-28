from langchain_core.runnables import RunnableWithMessageHistory
from langchain.memory import ChatMessageHistory
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import os
from langchain_chroma import Chroma
from typing import Literal, List
from langchain.schema.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
import requests
from langchain.tools import StructuredTool
from pydantic import BaseModel
from typing import List
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import RetrievalQA
from dotenv import load_dotenv

load_dotenv()
# Create Structured Tool

BASE_URL = "http://127.0.0.1:8000"


class FoodMenu(BaseModel):
    name: str
    description: str
    price: int


class EmptyInput(BaseModel):
    pass


class FoodMenuInput(BaseModel):
    data: FoodMenu


class OrderModel(BaseModel):
    customer_name: str
    item_id: int
    quantity: int


class OrderInput(BaseModel):
    data: OrderModel

# Tools


def get_menu() -> List[FoodMenu]:
    """Get menu Item of Indian Restaurant App
    this will return an menu items with price
    """
    url = BASE_URL+"/menu"
    response = requests.get(url)
    return response.json()


get_menu_tool = StructuredTool.from_function(
    func=get_menu,
    name="get_menu_tool",
    description="It get the menu list",
    args_schema=EmptyInput
)


def create_menu(data: FoodMenuInput):
    """Create menu Function, you can create menu from this fuction

    args:
        name:str
        description:str
        price:int
    """
    url = BASE_URL+"/menu"
    response = requests.post(url, json=data.model_dump())
    return response.json()


create_menu_tool = StructuredTool.from_function(
    func=create_menu,
    name='create_menu_tool',
    description="It create an menu",
    args_schema=FoodMenuInput
)


# Order Tool

# get list Of Orders.
def get_orders() -> List[OrderModel]:
    url = BASE_URL+"/orders"
    response = requests.get(url)
    return response.json()


get_order_tool = StructuredTool.from_function(
    func=get_orders,
    name="get_order_tool",
    description="Get Orders",
    args_schema=EmptyInput
)
# Create Order Tool


def create_order(data: OrderModel) -> OrderModel:
    url = BASE_URL+"/orders"
    response = requests.post(url, json=data.model_dump())
    return response.json()


create_order_tool = StructuredTool.from_function(
    func=create_order,
    name="create_order_tool",
    description="Create Order Tool",
    args_schema=OrderInput
)


# class ChatMessages:
#     messages: List[Messages]


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
        self.llm_with_tools = self.llm.bind_tools(
            [get_menu_tool, create_menu_tool, get_order_tool, create_order_tool])
        self.history_store = {}

    def get_history(self, session_id):
        if session_id not in self.history_store:
            self.history_store[session_id] = ChatMessageHistory()
        return self.history_store[session_id]

    def invoke(self, session_id: str, messages, input: str,) -> str:
        retriever = self.vector_store.as_retriever()
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", """
                    "You are a Restaurant App Support Tool"
                    "Use the given context to answer the question. "
                    "If you don't know the answer, say you don't know. "
                    "Use three sentence maximum and keep the answer concise. "
                    "Context: {context}"
                                """),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}")
            ]
        )
        chain = prompt | self.llm_with_tools | self.parser
        chain_with_history = RunnableWithMessageHistory(
            chain,
            get_session_history=lambda session_id: self.get_history(
                session_id),
            input_messages_key="input",
            history_messages_key="chat_history"
        )
        result = chain_with_history.invoke(
            {"input": input}, config={"configurable": {"session_id": session_id}})
        print(">>>>>>>>>>>>>>>>>>Result:", result)
        return "OU"
