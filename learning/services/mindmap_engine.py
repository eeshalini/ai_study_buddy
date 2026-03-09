import json
import re
from .index_manager import load_document_index
from .gemini_client import generate_response


def extract_json_from_text(text):
    """
    Extract first valid JSON object from text.
    """
    if text is None:
        return None
        
    # Remove markdown code blocks
    text = re.sub(r"```json|```", "", text)

    # Find first {...} block
    match = re.search(r"\{.*\}", text, re.DOTALL)

    if not match:
        return None

    json_str = match.group()

    # Remove trailing commas (common LLM issue)
    json_str = re.sub(r",\s*}", "}", json_str)
    json_str = re.sub(r",\s*]", "]", json_str)

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None


def generate_mindmap(user_id, document_id, map_type='overview'):
    index, chunks = load_document_index(user_id, document_id)

    if index is None:
        return None

    content = "\n".join(chunks[:6])
    
    if map_type == 'detailed':
        instruction = "Create a DETAILED BREAKDOWN mindmap. You MUST extract deep, comprehensive explanations. Your 'title' values should be full sentences or detailed phrases explaining the matter. Your structure must be highly nested (up to 4 levels deep) to capture all nuance."
    elif map_type == 'takeaways':
        instruction = "Create a KEY TAKEAWAYS mindmap. You MUST extract only the most critical highlights, conclusions, and important points. Keep the structure relatively flat (only 1 or 2 levels deep). Focus on actionable or conclusive statements."
    else:
        # Default to overview
        instruction = "Create a CONCEPT OVERVIEW mindmap. You MUST construct the main structure using ONLY SINGLE KEYWORDS or very short 2-3 word phrases. Do not use full sentences. Provide a high-level bird's-eye view of the document."

    prompt = f"""
    Generate a structured study mindmap in STRICT JSON format based on the content below.
    
    INSTRUCTION:
    {instruction}

    RULES for JSON output:
    1. ALWAYS wrap your ENTIRE output in `{{"title": "...", "type": "...", "children": [...] }}`
    2. Every node must have a `title` (text to display) and `type` (context, e.g. 'Core Concept', 'Category', 'Example')
    3. `children` is an array of sub-nodes. If a node has no children, omit the `children` key or use an empty array `[]`.
    4. ONLY return valid JSON. Do not include markdown code block wrappers like ```json.
    
    EXAMPLE JSON FORMAT:
    {{
      "title": "Main Topic",
      "type": "Core Concept",
      "children": [
        {{
          "title": "Subtopic",
          "type": "Category",
          "children": [
            {{"title": "Key Point", "type": "Detail/Example"}}
          ]
        }}
      ]
    }}

    Content to analyze:
    {content}
    """

    response = generate_response(prompt)

    parsed = extract_json_from_text(response)

    return parsed