import re
import spacy
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
import gc
import json

def clean_text(text):
   # Remove extra spaces (including tabs and multiple spaces)
   text = re.sub(r'\s+', ' ', text)
   
   # Remove line breaks
   text = text.replace('\n', ' ')
   
   # Trim leading and trailing spaces
   text = text.strip()
   
   return text


def split_text(text):
    # Remove punctuation, lowercase everything
    text = re.sub(r'[^\w\s]', '', text.lower())
    return text.split()  # Split into words


def extract_keywords(text, lang ):
    # Load medium Spacy model (better than small for NLP tasks)

    min_word_length = 3
    top_n = 10

    # Preprocess with Spacy
    if(lang == "es"):
        nlp_es = spacy.load("es_core_news_md")
        doc = nlp_es(text.lower())
    elif(lang == "en"):
        nlp_en = spacy.load("en_core_web_md")
        doc = nlp_en(text.lower())
    
    
    # Extract meaningful tokens
    keywords = [
        token.lemma_ for token in doc
        if not token.is_stop
        and not token.is_punct
        and len(token.text) >= min_word_length
        and token.pos_ in ["NOUN", "PROPN", "VERB", "ADJ"]  # Nouns, verbs, adjectives
    ]
    
    # Add noun chunks (phrases like "machine learning")
    keywords += [chunk.text for chunk in doc.noun_chunks]
    
    # TF-IDF filtering
    vectorizer = TfidfVectorizer(ngram_range=(1, 2))  # Include bigrams
    tfidf = vectorizer.fit_transform([" ".join(keywords)])
    feature_array = vectorizer.get_feature_names_out()
    tfidf_scores = tfidf.toarray()[0]
    
    # Get top scored keywords
    scored_keywords = sorted(
        zip(feature_array, tfidf_scores),
        key=lambda x: x[1],
        reverse=True
    )

    # Unload
    if(lang == "es"):
        del nlp_es  # Remove reference
    elif(lang == "en"):
        del nlp_en  # Remove reference
    
    gc.collect()  # Force garbage collection
    
    
    return [kw for kw, score in scored_keywords[:top_n]]


def calculate_job_match(profile, keywords):
    if not keywords:  # Prevent division by zero
        return 0
    
    matches = [
        kw for kw in keywords 
        if kw in profile.lower()
    ]
    
    match_percentage = (len(matches) / len(keywords)) * 100
    return round(match_percentage)


def format_resume_to_plain_text(profile_data: dict, to_AI: bool = False) -> str:
    """Convert JSON resume data to formatted plain text."""
    multiplier = 0
    line_break = ""
    if(not to_AI):
        multiplier = 40
        line_break = "\n"
    
    resume_lines = []
    
    # Header
    resume_lines.append("PROFESSIONAL PROFILE ")
    resume_lines.append("=" * multiplier)
    
    # Education
    if len(profile_data['education']) > 0:
        resume_lines.append(line_break+"EDUCATION ")
        resume_lines.append("-" * multiplier)
        for edu in profile_data['education']:
            start = f"{edu['graduationStartDate']['month']}/{edu['graduationStartDate']['year']}"
            end = f"{edu['graduationEndDate']['month']}/{edu['graduationEndDate']['year']}"
            resume_lines.append(
                f"{edu['degree']} - {edu['institution']} ({start} to {end}) "
            )
    
    # Work Experience
    if len(profile_data['jobs']) > 0:
        resume_lines.append(line_break+"WORK EXPERIENCE ")
        resume_lines.append("-" * multiplier)
        for job in profile_data['jobs']:
            start = f"{job['startDate']['month']}/{job['startDate']['year']}"
            end = f"{job['endDate']['month']}/{job['endDate']['year']}"
            resume_lines.append(
                f"{job['title']} at {job['company']} ({start} to {end}) "
            )
            resume_lines.append(f"Responsibilities: {job['responsibilities']} ")
    
    # Projects
    if len(profile_data['projects']) > 0:
        resume_lines.append(line_break+"PROJECTS ")
        resume_lines.append("-" * multiplier)
        for project in profile_data['projects']:
            resume_lines.append(
                f"{project['name']} - Technologies: {project['technologies']} "
            )
            resume_lines.append(f"Description: {project['description']} \n")
    
    # Skills
    if len(profile_data['skills']) > 0:
        resume_lines.append(line_break+"SKILLS ")
        resume_lines.append("-" * multiplier)
        resume_lines.append(", ".join(profile_data['skills']))
    
    return line_break.join(resume_lines)



def to_json(json_str: str) -> dict:
    try:
        # Step 1: Remove problematic control characters
        json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)
        
        # Step 2: Ensure proper escaping for common issues
        json_str = json_str.replace('\\', '\\\\')  # Escape existing backslashes
        json_str = json_str.replace('\n', '\\n')   # Escape newlines
        json_str = json_str.replace('\t', '\\t')   # Escape tabs
        
        # Step 3: Handle Unicode characters properly
        json_str = json_str.encode('unicode-escape').decode('ascii')
        json_str = json_str.replace('\\"', '"')  # Fix over-escaped quotes
        
        # Step 4: Final JSON parse with strict validation
        return json.loads(json_str)
    except Exception as e:
        return {}