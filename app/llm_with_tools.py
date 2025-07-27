import os
from langchain_chroma import Chroma
from typing import Literal, List
from langchain.schema.messages import HumanMessage, AIMessage, ToolMessage
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

    def invoke(self, messages) -> str:
        retriever = self.vector_store.as_retriever()
        chain = RetrievalQA.from_llm(retriever=retriever, llm=self.llm_with_tools,
                                     return_source_documents=True)
        result = chain.invoke(messages)
        return result['result']
