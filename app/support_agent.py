from langchain.tools import tool
from langchain.memory.buffer import ConversationBufferMemory
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
import os
from typing import List
from langchain.schema.messages import SystemMessage
import requests
from langchain.tools import StructuredTool
from pydantic import BaseModel
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


@tool
def get_current_time() -> str:
    """Returns the current system time."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool
def greet(name: str) -> str:
    """Greets a user by name."""
    return f"Hello, {name}!"


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
    description="Use this to get the list of menu items from the restaurant.",
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

WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')


@tool
def get_weather_data(city: str) -> str:
    """ get Weather Data
    args:
        city:str
    """
    url = f"https://api.weatherstack.com/current?access_key={WEATHER_API_KEY}&query={city}"
    response = requests.get(url)
    return response.json()


class LLMWithTools:
    def __init__(self) -> None:
        self.llm = ChatOpenAI(model="gpt-3.5-turbo")
        self.tools = [get_weather_data, get_current_time, greet,
                      get_menu_tool, create_menu_tool, get_order_tool, create_order_tool]
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="You are a helpful assistant."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        self.memory = ConversationBufferMemory(
            return_messages=True, memory_key="chat_history")
        self.agent = create_openai_functions_agent(
            llm=self.llm, tools=self.tools, prompt=self.prompt)
        self.agent_executor = AgentExecutor(
            agent=self.agent, tools=self.tools, memory=self.memory, verbose=True)

    def get_history(self, messages) -> ChatMessageHistory:
        chat_history = ChatMessageHistory()
        for msg in messages:
            chat_history.add_message(msg)
        return chat_history

    def invoke(self, messages, input: str,) -> str:
        chat_history = self.get_history(messages)
        self.memory.chat_memory.messages = chat_history.messages
        response = self.agent_executor.invoke(
            {'input': input})
        return response['output'] if 'output' in response else ''
