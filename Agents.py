from langchain.agents import create_agent
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, scrape_url
from rich import print
import os
from dotenv import load_dotenv
load_dotenv()
from langchain_groq import ChatGroq
# model setup
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

# 1st Agent
def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search]
    )

# 2nd Agent
def build_reader_agent():
    return create_agent(
        model = llm,
        tools=[scrape_url]
    )

# writer chain
writer_prompt = ChatPromptTemplate.from_messages([
    ("system","You are an expert research writer. Write clear, structure and insightful report."),
    ("human",""" Write a detailed Research report on the topic below:

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional."""),

])

writer_chain = writer_prompt | llm | StrOutputParser()

# critic_chain
critic_prompt = ChatPromptTemplate.from_messages([
    ("system","You are a sharp and Constructive research critic. Be honest and specific."),
    ('human',"""Review the research report below and evaluate and strictly.

Report:
{report}
     
Respond in this exact format:
     
Score: x/10
     
Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...
     
One line verdict:
..."""),
])

critic_chain = critic_prompt | llm | StrOutputParser()

