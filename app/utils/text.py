import re
import json
from datetime import datetime

def clean_text(text):
   # Remove extra spaces (including tabs and multiple spaces)
   text = re.sub(r'\s+', ' ', text)
   
   # Remove line breaks
   text = text.replace('\n', ' ')
   
   # Trim leading and trailing spaces
   text = text.strip()
   
   return text


def to_json(json_str: str) -> dict:
    try:
        return json.loads(json_str)
    
    except Exception as e:
        print(f"Error parsing JSON: {e}\n{json_str}")
        return {}
    


def process_ats_score(ats_data: dict, keywords: dict) -> dict:
    try:
        # Keyword Score (50%)
        full_matches = ats_data["keyword_analysis"]["full_matches"]
        half_matches = [m for m in ats_data["keyword_analysis"]["half_matches"] if m["section"] != "missing"]
        isolated_keywords = ats_data["keyword_analysis"]["isolated_keywords"]

        # Add matches into Keywords
        full_match_kws = [fm["keyword"] for fm in full_matches]
        half_match_kws = [hm["keyword"] for hm in half_matches]

        for item in keywords:
            kw = item["keyword"]
            item["matched"] = (kw in full_match_kws) or (kw in half_match_kws)
            item["half"] = kw in half_match_kws

        print("full matches are:")
        print(full_match_kws)
        print("half matches are:")
        print(half_match_kws)
        print("final kw dict is: ")
        print(keywords)
        
        keyword_score = min(
            max(
            (len(full_matches) * 2) + 
            (len(half_matches) * 1) - 
            (len(isolated_keywords) * 1),
            0  # Prevent negative scores
        ), 50)

        # Structure Score (30%) - UNIVERSAL RULES
        structure_score = 30
        missing_sections = ats_data["structure_analysis"]["missing_sections"]
        
        # Mandatory for all industries
        for section in ["work", "skills", "education"]:
            if section in missing_sections:
                structure_score -= 10
        
        # Optional sections (no penalty if missing)
        structure_score = min(max(structure_score, 0), 30)

        # Readability Score (20%) - UNIVERSAL RULES
        readability_score = 20
        readability_score -= ats_data["readability_analysis"]["long_bullets"] * 2  # -2 per long bullet
        if ats_data["readability_analysis"].get("has_tables_graphics", False):
            readability_score -= 10  # Heavy penalty for ATS-unfriendly formats
        if ats_data["readability_analysis"]["action_verb_compliance"] < 0.9:
            readability_score -= 2
        if len(ats_data["readability_analysis"]["keyword_positioning"]["missing_in_first_third"]) > 0:
            readability_score -= 3
        
        readability_score = min(max(readability_score, 0), 20)

        # Industry-Specific Tips (Optional)
        tips = ats_data.get("tips", [])

        ats_keyword_score = (keyword_score / 50) * 100
        ats_structure_score = (structure_score / 30) * 100
        ats_readability_score = (readability_score / 20) * 100

        ats_score = (
                    (ats_keyword_score * 0.50) + 
                    (ats_structure_score * 0.30) + 
                    (ats_readability_score * 0.20))

        return {
            "ats": {
                "ats_score": min(max(ats_score, 0), 100),
                "breakdown": {
                    "keyword_match": min(max(ats_keyword_score, 0), 100),
                    "structure": min(max(ats_structure_score, 0), 100),
                    "readability": min(max(ats_readability_score, 0), 100),
                },
                "tips": tips
            },
            "keywords": keywords
        }
    except Exception as e:
        print(e)
        return {}


def firestore_to_datetime(fs_date):
    if not fs_date:
        return None
    # If it's already a datetime (or compatible), return as-is
    if isinstance(fs_date, datetime):
        return fs_date
    # Handle DatetimeWithNanoseconds (access attributes directly)
    return datetime(
        fs_date.year, fs_date.month, fs_date.day,
        fs_date.hour, fs_date.minute, fs_date.second
    )