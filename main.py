#packages to import

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import create_agent



#load the .env
load_dotenv()


#openrouter uses OPENAI
#NVIDIA model since better at agent stuff
#temperature means creativity
#higher temperature means more creativity and randomness 
#0 is ground truth, tries to use what it knows.
llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    model="nvidia/nemotron-3-nano-30b-a3b:free",
    temperature=0.0
)


#create system prompt, it's what it reads prior before what it asks the question
SYSTEM_MESSAGE = """
You are a helpful coding assistant with the ability to write code in Python and actually EXECUTE the code.
You have access to a tool called "execute_code" that takes a string of code and executes it.
You must only write code in Python.
You may decide to execute code to obtain output and use it in your response.

Rules:
- Only generate safe Python code.
- Do not generate any code that will loop infinitely or cause a crash.
- Never access files or the operating system
- Never import modules that affect the operating system like os, sys, subprocess, socket, or shutil.
"""


# something you DON'T need to do, but you should
#guardrails is a safety mechanism
#list of keywords that if the tool uses,it'll stop tool and say "hey you can't use this keyword!"

#niche, good to know!
GUARDRAIL = [
    "import os",
    "import sys",
    "import subprocess",
    "import socket",
    "import shutil",
    "open(",
    "__import__",
    "eval(",
    "exec("
]


#creating the tool
#using exec


#docstring, decorato, 
#Tool Decorator
# use code:str -> str so you know you PASS a string and RETURN a string

@tool
def execute_code(code: str) -> str:
    """Used to execute code and retrieve the output of the codeblock"""

    for word in GUARDRAIL:
        if word in code:
            return f"Code Execution Blocked: Contained Forbidden Word '{word}'."

    try:
        local_variables = {}
        exec(code, local_variables)
        return f"Code Execution Successful: {str(local_variables)}"
    except Exception as ex:
        return f"Code Execution Failed with Error: {ex}"

#creating agent

agent = create_agent(
    model= llm,
    tools = [execute_code],
)

messages = [
    SystemMessage(content=SYSTEM_MESSAGE),
    HumanMessage(content="Calculate compound interest on $9000 at 12 percent for 6 years. SHow me the code and the result.")
]

response = agent.invoke({"messages": messages})
print(response["messages"][-1].content)