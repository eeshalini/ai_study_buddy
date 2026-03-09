import os
import django
import sys
import json
import time

# Setup Django env
sys.path.append(r"C:\Users\Pavan Kumar\Desktop\Ai Study Buddy(8-3)\adaptive_rag")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from learning.models import StudyDocument, User
from learning.services.index_manager import load_document_index
from learning.services.gemini_client import generate_response

def test_mindmap_types():
    user = User.objects.first()
    doc = StudyDocument.objects.first()
    
    if not doc:
        print("No document found in database.")
        return
        
    index, chunks = load_document_index(user.id, doc.id)
    if not index:
        return
    content = "\n".join(chunks[:6])

    print(f"Testing document: {doc.title} (ID: {doc.id})")
    
    # Accept type from command line to avoid rate limits
    if len(sys.argv) > 1:
        types = [sys.argv[1]]
    else:
        types = ['detailed']
        
    results = {}
    
    with open('mindmap_test_log.txt', 'w', encoding='utf-8') as log_file:
        for map_type in types:
            print(f"\n--- Generating {map_type} ---")
            log_file.write(f"\n--- Generating {map_type} ---\n")
            try:
                # Sleep to bypass Gemini strict free-tier limits
                print("Waiting 15 seconds for API limits...")
                time.sleep(15)
                
                if map_type == 'detailed':
                    instruction = "Create a DETAILED BREAKDOWN mindmap. You MUST extract deep, comprehensive explanations. Your 'title' values should be full sentences or detailed phrases explaining the matter. Your structure must be highly nested (up to 4 levels deep) to capture all nuance."
                elif map_type == 'takeaways':
                    instruction = "Create a KEY TAKEAWAYS mindmap. You MUST extract only the most critical highlights, conclusions, and important points. Keep the structure relatively flat (only 1 or 2 levels deep). Focus on actionable or conclusive statements."
                else:
                    instruction = "Create a CONCEPT OVERVIEW mindmap. You MUST construct the main structure using ONLY SINGLE KEYWORDS or very short 2-3 word phrases. Do not use full sentences. Provide a high-level bird's-eye view of the document."

                prompt = f"""
                Generate a structured study mindmap in STRICT JSON format based on the content below.
                INSTRUCTION: {instruction}
                RULES: 1. ALWAYS wrap output in {{"title": "...", "type": "...", "children": [...] }}
                Content: {content}
                """
                
                response = generate_response(prompt)
                
                # Print brief stats
                if response:
                    print(f"SUCCESS: Raw String ({len(response)} chars)")
                    log_file.write(f"SUCCESS: Raw String ({len(response)} chars)\n")
                    log_file.write(response + "\n")
                else:
                    print("FAILED: API Response was None.")
                    log_file.write("FAILED: API Response was None.\n")
            except Exception as e:
                print(f"ERROR: {e}")
                log_file.write(f"ERROR: {e}\n")

if __name__ == '__main__':
    test_mindmap_types()
