import os
import json
from dotenv import load_dotenv, find_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.memory import ConversationBufferMemory

# Load Environment
load_dotenv(find_dotenv())

ROLE_MAP = {
    "General Assistant": "You are a helpful student assistant.",
    "Math Tutor": "You are a patient math tutor.",
    "Science Tutor": "You are a science tutor.",
    "Language Teacher": "You are a supportive language teacher.",
    "Career Counselor": "You are a helpful career counselor."
}

# Initialize LLM
api_key = os.getenv("GROQ_API_KEY")
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.7, groq_api_key=api_key)

class ChatbotWithMemory:
    def __init__(self, memory_file="chat_memory.json"):
        self.memories = {}
        self.memory_file = memory_file
        self.load_memory()
    
    def load_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    for key, msgs in data.items():
                        mem = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
                        for m in msgs:
                            if m['type'] == 'human': mem.chat_memory.add_user_message(m['content'])
                            else: mem.chat_memory.add_ai_message(m['content'])
                        self.memories[key] = mem
            except: pass

    def save_memory(self):
        data = {k: [{'type': 'human' if m.type == 'human' else 'ai', 'content': m.content} 
                for m in v.chat_memory.messages] for k, v in self.memories.items()}
        with open(self.memory_file, 'w') as f:
            json.dump(data, f, indent=2)

    def get_chat_response(self, user_input, role, user_name):
        if not user_input or not user_input.strip(): return ""
        
        memory_key = f"{user_name}_{role}"
        if memory_key not in self.memories:
            self.memories[memory_key] = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
        mem = self.memories[memory_key]
        history = mem.load_memory_variables({})["chat_history"]
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"{ROLE_MAP.get(role)} Student: {user_name}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        
        chain = prompt | llm
        response = chain.invoke({"input": user_input, "chat_history": history})
        
        mem.chat_memory.add_user_message(user_input)
        mem.chat_memory.add_ai_message(response.content)
        self.save_memory()
        return response.content

# --- MODULE EXPORTS ---
bot = ChatbotWithMemory()

def get_chat_response(user_input, role, user_name="Student"):
    return bot.get_chat_response(user_input, role, user_name)

def clear_chat_history(user_name, role):
    key = f"{user_name}_{role}"
    if key in bot.memories:
        bot.memories[key].clear()
        del bot.memories[key]
        bot.save_memory()
    return True

def get_conversation_summary(user_name, role):
    key = f"{user_name}_{role}"
    if key in bot.memories:
        msgs = bot.memories[key].chat_memory.messages
        return {"total_messages": len(msgs)}
    return {"total_messages": 0} 