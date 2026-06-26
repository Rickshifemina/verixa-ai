import re

def calculate_ats_score(resume_text, jd_text):
    """Calculate ATS score based on keyword matching"""
    # Clean and tokenize text
    resume_words = set(re.findall(r'\b[a-zA-Z]+\b', resume_text.lower()))
    jd_words = set(re.findall(r'\b[a-zA-Z]+\b', jd_text.lower()))
    
    # Remove common stop words
    stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                  'of', 'with', 'by', 'from', 'as', 'is', 'was', 'were', 'are', 'be'}
    
    resume_words = resume_words - stop_words
    jd_words = jd_words - stop_words
    
    if not jd_words:
        return 0, []
    
    # Calculate matched keywords
    matched_keywords = resume_words.intersection(jd_words)
    missing_keywords = list(jd_words - resume_words)
    
    # Calculate score
    score = (len(matched_keywords) / len(jd_words)) * 100
    
    return round(score, 2), sorted(missing_keywords)[:15]  # Return top 15 missing keywords 