import streamlit as st
from chatbot import get_chat_response, clear_chat_history,get_conversation_summary, ROLE_MAP
from ats_checker import check_ats
from coding_assistant import get_code_help
from research_tool import research_topic
from notes_generator import generate_notes
import time

# Page configuration
st.set_page_config(
    page_title="VERIXA AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
    }
    .success-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #f0f8ff;
        border-left: 5px solid #4CAF50;
    }
    .warning-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
    }
    .info-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #d1ecf1;
        border-left: 5px solid #17a2b8;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .user-message {
        background-color: #e3f2fd;
    }
    .assistant-message {
        background-color: #f1f3f4;
    }
    .stat-box {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        border-left: 3px solid #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("🎓 VERIXA AI - Student Super Assistant")
st.markdown("---")

# Initialize all session state variables
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "research_history" not in st.session_state:
    st.session_state.research_history = []
if "notes_history" not in st.session_state:
    st.session_state.notes_history = []
if "coding_history" not in st.session_state:
    st.session_state.coding_history = []
if "current_user" not in st.session_state:
    st.session_state.current_user = "Student"
if "current_role" not in st.session_state:
    st.session_state.current_role = "General Assistant"
if "show_clear_confirmation" not in st.session_state:
    st.session_state.show_clear_confirmation = False
if "last_response_time" not in st.session_state:
    st.session_state.last_response_time = time.time()

# Sidebar navigation
with st.sidebar:
    st.markdown("# 🎓")
    st.title("Navigation")
    
    menu = st.radio(
        "Select Tool",
        [
            "AI Chatbot",
            "ATS Resume Checker",
            "Coding Assistant",
            "Research Tool",
            "AI Study Notes Generator"
        ],
        key="main_menu"
    )
    
    st.markdown("---")
    
    # User profile section
    with st.expander("👤 User Profile", expanded=False):
        user_name = st.text_input("Your name", value=st.session_state.current_user)
        if user_name != st.session_state.current_user:
            st.session_state.current_user = user_name
            st.rerun()
    
    st.markdown("### About")
    st.info("Verixa AI helps students with learning, coding, career, and research!")
    
    # Show recent activity based on current menu
    if menu == "AI Chatbot" and st.session_state.chat_history:
        with st.expander("💬 Recent Chat"):
            last_messages = st.session_state.chat_history[-4:]
            for msg in last_messages:
                if msg["role"] == "user":
                    st.chat_message("user").write(msg["content"])
                else:
                    st.chat_message("assistant").write(msg["content"])
    
    elif menu == "Research Tool" and st.session_state.research_history:
        with st.expander("📚 Recent Research"):
            for i, item in enumerate(st.session_state.research_history[-3:]):
                st.write(f"{i+1}. {item}")
    
    elif menu == "AI Study Notes Generator" and st.session_state.notes_history:
        with st.expander("📝 Recent Notes"):
            for i, topic in enumerate(st.session_state.notes_history[-3:]):
                st.write(f"{i+1}. {topic}")
    
    elif menu == "Coding Assistant" and st.session_state.coding_history:
        with st.expander("👨‍💻 Recent Coding"):
            for i, problem in enumerate(st.session_state.coding_history[-3:]):
                st.write(f"{i+1}. {problem[:20]}...")
    
    st.markdown("---")
    st.caption(f"👤 Logged in as: **{st.session_state.current_user}**")

# Main content area
if menu == "AI Chatbot":
    st.header("💬 AI Chatbot")
    st.markdown("Chat with AI in different modes - **with memory!** The bot remembers your conversation.")
    
    # Settings in columns
    col1, col2 = st.columns([1, 3])
    
    with col1:
        role = st.selectbox(
            "Chatbot Mode",
            list(ROLE_MAP.keys()),
            key="chatbot_role"
        )
        
        # Update session state when role changes
        if role != st.session_state.current_role:
            st.session_state.current_role = role
        
        # Chat controls
        st.markdown("### Controls")
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            if st.session_state.chat_history:
                st.session_state.show_clear_confirmation = True
        
        if st.session_state.show_clear_confirmation:
            st.warning("Are you sure you want to clear all chat history?")
            col1_1, col1_2 = st.columns(2)
            with col1_1:
                if st.button("✅ Yes", key="confirm_clear"):
                    clear_chat_history(st.session_state.current_user, role)
                    st.session_state.chat_history = []
                    st.session_state.show_clear_confirmation = False
                    st.rerun()
            with col1_2:
                if st.button("❌ No", key="cancel_clear"):
                    st.session_state.show_clear_confirmation = False
                    st.rerun()
        
        if st.button("💾 Export Chat", use_container_width=True) and st.session_state.chat_history:
            chat_text = "\n\n".join([
                f"{msg['role'].upper()}: {msg['content']}"
                for msg in st.session_state.chat_history
            ])
            st.download_button(
                label="Download Chat",
                data=chat_text,
                file_name=f"chat_{st.session_state.current_user}_{role}.txt",
                mime="text/plain"
            )
        
        # Conversation stats
        if st.session_state.chat_history:
            st.markdown("### Stats")
            user_msgs = len([m for m in st.session_state.chat_history if m["role"] == "user"])
            assistant_msgs = len([m for m in st.session_state.chat_history if m["role"] == "assistant"])
            st.caption(f"💬 {user_msgs} questions • {assistant_msgs} responses")
    
    with col2:
        # Display chat history
        chat_container = st.container()
        with chat_container:
            if not st.session_state.chat_history:
                st.info(f"👋 Hello {st.session_state.current_user}! I'm your {role}. How can I help you today?")
            
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
    
# Chat input
    user_input = st.chat_input(f"Ask your {role} something...")
    
    if user_input:
        # 1. Store user message
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # 2. Get bot response
        with st.spinner(f"{role} is processing your request..."):
            response = get_chat_response(
                user_input,
                role,
                st.session_state.current_user
            )
        
        # 3. Store bot response
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # 4. IMPORTANT: DO NOT USE ST.RERUN() HERE. 
        # Streamlit naturally reruns when session_state changes.
        # Calling st.rerun() manually inside a chat input often triggers the infinite loop.

elif menu == "ATS Resume Checker":
    st.header("📄 ATS Resume Checker")
    st.markdown("Check how well your resume matches a job description")
    
    col1, col2 = st.columns(2)
    
    with col1:
        resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    
    with col2:
        jd_text = st.text_area("Paste Job Description", height=200)
    
    if st.button("🔍 Check ATS Score", use_container_width=True):
        if resume_file is not None and jd_text.strip():
            with st.spinner("Analyzing your resume..."):
                result = check_ats(resume_file, jd_text)
            
            st.markdown("---")
            st.markdown("### 📊 Analysis Results")
            
            # Display score with color
            try:
                score_value = int(result["ATS Score"].replace("%", ""))
                if score_value >= 80:
                    st.success(f"**ATS Score:** {result['ATS Score']} - Excellent match!")
                elif score_value >= 60:
                    st.warning(f"**ATS Score:** {result['ATS Score']} - Good, but can improve")
                else:
                    st.error(f"**ATS Score:** {result['ATS Score']} - Needs improvement")
            except:
                st.info(f"**ATS Score:** {result['ATS Score']}")
            
            # Display missing keywords
            if result.get("Missing Keywords"):
                st.markdown("**Missing Keywords:**")
                keywords = ", ".join(result["Missing Keywords"])
                st.info(keywords)
            
            # Display suggestions
            if result.get("AI Suggestions"):
                st.markdown("**💡 AI Suggestions:**")
                with st.expander("View Suggestions"):
                    st.markdown(result["AI Suggestions"])
                    
                    st.download_button(
                        label="📥 Download Suggestions",
                        data=result["AI Suggestions"],
                        file_name="ats_suggestions.txt",
                        mime="text/plain"
                    )
        else:
            st.warning("Please upload a resume and paste a job description.")

elif menu == "Coding Assistant":
    st.header("👨‍💻 Coding Assistant")
    st.markdown("Get help with your coding problems")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        language = st.selectbox(
            "Programming Language",
            ["Python", "JavaScript", "Java", "C++", "HTML/CSS", "SQL"]
        )
        
        # Show coding history
        if st.session_state.coding_history:
            with st.expander("📜 Recent Problems"):
                for i, problem in enumerate(st.session_state.coding_history[-5:]):
                    if st.button(f"🔄 {problem[:30]}...", key=f"recent_code_{i}"):
                        st.session_state.code_problem = problem
                        st.rerun()
    
    with col2:
        code_problem = st.text_area(
            "Describe your coding problem",
            height=150,
            placeholder="Example: How do I reverse a string in Python? Write a function to find prime numbers...",
            key="code_problem_input"
        )
        
        complexity = st.select_slider(
            "Solution Complexity",
            options=["Simple", "Moderate", "Detailed"],
            value="Moderate"
        )
    
    if st.button("💡 Get Help", use_container_width=True) and code_problem.strip():
        # Add to history
        if code_problem not in st.session_state.coding_history:
            st.session_state.coding_history.append(code_problem)
        
        with st.spinner(f"Generating {complexity.lower()} solution..."):
            response = get_code_help(code_problem, language)
        
        st.markdown("---")
        st.markdown("### Solution:")
        
        tab1, tab2 = st.tabs(["💻 Code Solution", "📝 Explanation"])
        with tab1:
            st.code(response, language=language.lower())
        with tab2:
            st.markdown(response)

elif menu == "Research Tool":
    st.header("🔬 Research & Analysis Tool")
    st.markdown("Research any topic and get structured information")
    
    tab1, tab2 = st.tabs(["🔍 New Research", "📚 Research History"])
    
    with tab1:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            topic = st.text_input(
                "Enter topic to research",
                placeholder="e.g., Quantum Computing, Photosynthesis, Python Programming",
                key="research_input"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            research_button = st.button("🔍 Research", use_container_width=True, type="primary")
        
        st.caption("⚠️ **Note:** To respect free API limits, searches are delayed. Please be patient.")
        
        with st.expander("💡 Suggested Topics"):
            suggestions = [
                "Artificial Intelligence", "Climate Change", "Photosynthesis",
                "Python Programming", "Machine Learning", "World War II"
            ]
            cols = st.columns(3)
            for i, suggestion in enumerate(suggestions):
                if cols[i % 3].button(suggestion, key=f"sugg_{i}"):
                    st.session_state.research_input = suggestion
                    st.rerun()
        
        if research_button and topic.strip():
            if topic not in st.session_state.research_history:
                st.session_state.research_history.append(topic)
            
            with st.spinner(f"Researching '{topic}'..."):
                result = research_topic(topic)
            
            st.markdown("---")
            st.markdown(f"### 📊 Research Results: {topic}")
            st.markdown(result)
            
            st.download_button(
                label="📥 Download Research",
                data=result,
                file_name=f"{topic}_research.txt",
                mime="text/plain"
            )
    
    with tab2:
        if st.session_state.research_history:
            for i, past_topic in enumerate(reversed(st.session_state.research_history)):
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button(f"📌 {past_topic}", key=f"past_{i}"):
                        with st.spinner(f"Researching '{past_topic}'..."):
                            result = research_topic(past_topic)
                        st.markdown("---")
                        st.markdown(f"### 📊 Research Results: {past_topic}")
                        st.markdown(result)
                with col2:
                    if st.button(f"❌ Remove", key=f"remove_{i}"):
                        st.session_state.research_history.remove(past_topic)
                        st.rerun()
        else:
            st.info("No research history yet.")

elif menu == "AI Study Notes Generator":
    st.header("📝 AI Study Notes Generator")
    st.markdown("Generate comprehensive study notes on any topic")
    
    col1, col2 = st.columns(2)
    
    with col1:
        topic = st.text_input(
            "Enter topic",
            placeholder="e.g., Photosynthesis, Python Loops, etc.",
            key="notes_topic"
        )
    
    with col2:
        level = st.selectbox(
            "Difficulty Level",
            ["Beginner", "Intermediate", "Advanced"],
            key="notes_level"
        )
    
    if st.button("📚 Generate Notes", use_container_width=True) and topic.strip():
        if topic not in st.session_state.notes_history:
            st.session_state.notes_history.append(topic)
        
        with st.spinner(f"Generating {level.lower()} level notes..."):
            notes = generate_notes(topic, level)
        
        st.markdown("---")
        st.markdown(f"### 📖 Study Notes: {topic} ({level} Level)")
        st.markdown(notes)
        
        st.download_button(
            label="📥 Download Notes",
            data=notes,
            file_name=f"{topic}_notes.txt",
            mime="text/plain"
        )
       

# Footer
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("Made with ❤️ for students")
with col2:
    st.markdown("Verixa AI v2.0")
with col3:
    st.markdown("[Report Issue](https://github.com)")
with col4:
    st.markdown(f"👤 User: {st.session_state.current_user}") 

