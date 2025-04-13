def extract_keywords_schema(rules: dict) -> dict:
    tools = [
    {
        "type": "function",
        "function": {
            "name": "extract_keywords",
            "description": f"""Extract keywords from the job description text and categorize them.
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
                                "job_description_language":{"type": "string"}
                            },
                            "required": ["keyword", "type", "count"],
                        },
                    }
                },
                "required": ["keywords"],
            },
        },
    }
    ]
    return tools