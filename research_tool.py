import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.3,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

search = DuckDuckGoSearchRun()

def research_topic(topic):
    """Research a topic and provide structured information"""
    
    try:
        # Search for information
        search_results = search.run(f"{topic} educational overview for students")
        
        # Generate summary
        summary_prompt = ChatPromptTemplate.from_template(
            """Summarize this information about {topic} for students:

{search_results}

Provide:
1. A simple explanation of {topic}
2. Key concepts to understand
3. Real-world applications
4. Why it's important for students to learn this"""
        )
        
        chain = summary_prompt | llm
        result = chain.invoke({"topic": topic, "search_results": search_results[:2000]})
        
        return result.content
        
    except Exception as e:
        return f"Error researching topic: {str(e)}" 