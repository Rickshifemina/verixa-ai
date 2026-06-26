import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.3,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

parser = StrOutputParser()

def get_code_help(question, language="Python"):
    """Get coding assistance"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are a coding assistant specialized in {language}.
        Provide clear, beginner-friendly explanations with code examples.
        If the question is not about {language}, politely redirect to ask about {language}."""),
        ("human", "{question}")
    ])
    
    chain = prompt | llm | parser
    response = chain.invoke({"question": question})
    
    return response 