def extract_keywords_schema(rules: dict) -> dict:
    tools = [{
        "type": "function",
        "function": {
            "name": "extract_keywords",
            "description": f"""{rules["task"]}.
            RULES:
            {'\n'.join(f'  - {r}' for r in rules["global_rules"]["formats"])}""",
            "parameters": {
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "keyword": {"type": "string"},
                                "type": {
                                    "type": "string",
                                    "enum": ["hard_skill", "soft_skill", "tool", "certification"],
                                },
                                "count": {"type": "integer"},
                            },
                            "required": ["keyword", "type", "count"],
                        },
                    },
                    "job_description_language":{"type": "string"}
                },
                "required": ["keywords", "job_description_language"],
            },
        },
    }
    ]
    return tools


def optimize_resume_schema(rules: dict) -> dict:
    tools = [{
        "type": "function",
        "function": {
            "name": "optimize_resume",
            "description": f"""{rules["task"]}.
            RULES:
            {'\n'.join(f'  - {r}' for r in rules["rules"])}""",
            "parameters": {
                "type": "object",
                "properties": {
                    "improvements":{
                        "type":"array",
                        "items":{
                            "type":"object",
                            "properties":{
                                "category":{"type":"string"},
                                "suggestions":{
                                    "type":"array",
                                    "items":{
                                        "type":"object",
                                        "properties":{
                                            "suggestion": {"type":"string"},
                                            "advice":{"type":"string"}
                                        },
                                        "required":["suggestion","advice"]
                                    }
                                }
                            },
                            "required":["category", "suggestions"]
                        }
                    },
                    "message":{"type": "string"}
                },
                "required": ["improvements", "message"],
            },
        },
    }
    ]
    return tools



def ats_score_schema(rules: dict) -> dict:
    tools = [{
        "type": "function",
        "function": {
            "name": "ats_score",
            "description": f"""{rules["task"]}.

            RULES:
            1.Keyword Validation:
            {'\n'.join(f'  - {r}' for r in rules["rules"]["keyword_validation"])}
            2.Context Rules:
            {'\n'.join(f'  - {r}' for r in rules["rules"]["context"])}
            3.Tips to improve:
               - Give your BEST tips to IMPROVE the score for this resume""",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword_analysis":{
                        "type": "object",
                        "properties":{
                            "full_matches":{
                                "type": "array",
                                "items":{
                                    "type":"object",
                                    "properties":{
                                        "keyword":{"type":"string"},
                                        "section":{"type":"string"},
                                        "context":{"type":"string"},
                                    },
                                    "required":["keyword","section","context"]
                                }
                            },
                            "half_matches":{
                                "type": "array",
                                "items":{
                                    "type":"object",
                                    "properties":{
                                        "keyword":{"type":"string"},
                                        "section":{"type":"string"},
                                    },
                                    "required":["keyword","section"]
                                }
                            },
                            "missing_keywords":{
                                "type": "array",
                                "items":{"type": "string"}
                            },
                            "isolated_keywords":{
                                "type": "array",
                                "items":{"type": "string"}
                            }
                        },
                        "required":["full_matches", "half_matches", "missing_keywords", "isolated_keywords"]
                    },
                    "structure_analysis":{
                        "type": "object",
                        "properties":{
                            "missing_sections":{
                                "type":"array",
                                "items":{"type":"string"},
                            },
                            "section_order":{
                                "type":"array",
                                "items":{"type":"string"},
                            },
                            "has_tables_graphics":{"type":"boolean"}
                        },
                        "required":["missing_sections","section_order","has_tables_graphics"]
                    },
                    "readability_analysis":{
                        "type":"object",
                        "properties":{
                            "long_bullets": {"type":"number"},
                            "action_verb_compliance": {"type":"number"},
                            "keyword_positioning":{
                                "type":"object",
                                "properties":{
                                    "critical_keywords_in_first_third":{
                                        "type":"array",
                                        "items":{"type":"string"},
                                    },
                                    "missing_in_first_third":{
                                        "type":"array",
                                        "items":{"type":"string"},
                                    },
                                },
                                "required":["critical_keywords_in_first_third", "missing_in_first_third"]
                            }
                        },
                        "required":["long_bullets", "action_verb_compliance", "keyword_positioning"]
                    },
                    "tips":{
                        "type":"array",
                        "items":{"type":"string"}
                    }
                },
                "required": ["keyword_analysis", "structure_analysis", "readability_analysis", "tips"],
            },
        },
    }
    ]
    return tools

