import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from utils.pdf_parser import extract_text_from_pdf
from utils.ats_score import calculate_ats_score

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.3,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

def check_ats(resume_file, job_description):
    """Check ATS score and provide suggestions"""
    try:
        # Extract text from PDF
        resume_text = extract_text_from_pdf(resume_file)
        
        if not resume_text:
            return {
                "ATS Score": "0%",
                "Missing Keywords": [],
                "AI Suggestions": "Could not extract text from PDF. Please ensure the PDF contains selectable text."
            }
        
        # Calculate ATS score
        score, missing_keywords = calculate_ats_score(resume_text, job_description)
        
        # Get AI suggestions
        prompt = f"""You are an ATS Resume Expert. Analyze this resume against the job description and provide specific improvement suggestions.

Resume:
{resume_text[:2000]}  # Limit text length

Job Description:
{job_description[:1000]}  # Limit text length

ATS Score: {score}%
Missing Keywords: {', '.join(missing_keywords[:10])}

Please provide:
1. Top 3 resume improvement suggestions
2. Key skills to add (from missing keywords)
3. Section-by-section improvements
4. Formatting and keyword optimization tips

Keep suggestions practical and actionable for students."""
        
        response = llm.invoke(prompt)
        
        return {
            "ATS Score": f"{score}%",
            "Missing Keywords": missing_keywords[:10],
            "AI Suggestions": response.content
        }
        
    except Exception as e:
        return {
            "ATS Score": "Error",
            "Missing Keywords": [],
            "AI Suggestions": f"An error occurred: {str(e)}"
        } 
