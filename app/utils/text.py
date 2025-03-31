import re
import spacy
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer

# Load medium Spacy model (better than small for NLP tasks)
nlp_es = spacy.load("es_core_news_md")
nlp_en = spacy.load("en_core_web_md")

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
   min_word_length = 3
   top_n = 10

   # Preprocess with Spacy
   if(lang == "es"):
      doc = nlp_es(text.lower())
   elif(lang == "en"):
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


def format_resume_to_plain_text(profile_data: dict) -> str:
    """Convert JSON resume data to formatted plain text."""
    resume_lines = []
    
    # Header
    resume_lines.append("PROFESSIONAL PROFILE")
    resume_lines.append("=" * 40)
    
    # Education
    resume_lines.append("\nEDUCATION")
    resume_lines.append("-" * 40)
    for edu in profile_data['education']:
        start = f"{edu['graduationStartDate']['month']}/{edu['graduationStartDate']['year']}"
        end = f"{edu['graduationEndDate']['month']}/{edu['graduationEndDate']['year']}"
        resume_lines.append(
            f"{edu['degree']} - {edu['institution']} ({start} to {end})"
        )
    
    # Work Experience
    resume_lines.append("\nWORK EXPERIENCE")
    resume_lines.append("-" * 40)
    for job in profile_data['jobs']:
        start = f"{job['startDate']['month']}/{job['startDate']['year']}"
        end = f"{job['endDate']['month']}/{job['endDate']['year']}"
        resume_lines.append(
            f"{job['title']} at {job['company']} ({start} to {end})"
        )
        resume_lines.append(f"Responsibilities: {job['responsibilities']}")
    
    # Projects
    resume_lines.append("\nPROJECTS")
    resume_lines.append("-" * 40)
    for project in profile_data['projects']:
        resume_lines.append(
            f"{project['name']} - Technologies: {project['technologies']}"
        )
        resume_lines.append(f"Description: {project['description']}\n")
    
    # Skills
    resume_lines.append("\nSKILLS")
    resume_lines.append("-" * 40)
    resume_lines.append(", ".join(profile_data['skills']))
    
    return "\n".join(resume_lines)