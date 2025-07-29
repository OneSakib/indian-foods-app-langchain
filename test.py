from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage
from langchain.tools import tool, StructuredTool
from pydantic import BaseModel
import requests
from dotenv import load_dotenv
load_dotenv()
# 1. Define LLM
llm = ChatOpenAI(model="gpt-4o")

# 2. Define Tools


@tool
def get_current_time() -> str:
    """Returns the current system time."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# -------------------- Your Custom Tool --------------------

BASE_URL = "http://127.0.0.1:8000"  # Update if needed

# Define your input model


class OrderModel(BaseModel):
    item_name: str
    quantity: int
    price: float


class OrderInput(BaseModel):
    data: OrderModel

# Create order function


def create_order(data: OrderModel):
    """Creates an order by sending data to the API endpoint."""
    url = BASE_URL + "/orders"
    response = requests.post(url, json=data.model_dump())
    return response.json()


# Wrap in a StructuredTool
create_order_tool = StructuredTool.from_function(
    func=create_order,
    name="create_order_tool",
    description="Create an order by providing item_name, quantity, and price.",
    args_schema=OrderInput
)

# -------------------- Example Tools --------------------


@tool
def greet(name: str) -> str:
    """Greets a user by name."""
    return f"Hello, {name}!"


tools = [get_current_time, greet, create_order_tool]
memory = ConversationBufferMemory(
    return_messages=True, memory_key="chat_history")
# 3. Define Prompt
prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="You are a helpful assistant."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

# 4. Create Agent
agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)
# 5. Create Executor
agent_executor = AgentExecutor(
    agent=agent, tools=tools, memory=memory, verbose=True)

# 6. Run Agent
if __name__ == "__main__":
    print("You can now chat with the agent. Type 'exit' to quit.\n")
    while True:
        user_input = input("User: ")
        if user_input.lower() == "exit":
            break

        response = agent_executor.invoke({"input": user_input})
        print("Agent:", response['output'])
