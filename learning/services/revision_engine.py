import json
import re
from .gemini_client import generate_response
from ..models import QuizAttempt, FlashCard, ChatMessage, StudyDocument
from django.db.models import Avg, F

def generate_revision_plan(user_id):
    """
    Analyzes a user's performance across all their documents to generate
    a comprehensive, personalized learning plan using Gemini.
    """
    
    # 1. Gather User's Context
    documents = StudyDocument.objects.filter(user_id=user_id)
    if not documents.exists():
        return None

    performance_data = []
    
    for doc in documents:
        attempts = QuizAttempt.objects.filter(user_id=user_id, document=doc)
        total_attempts = attempts.count()
        
        avg_score = 0
        if total_attempts > 0:
            total_earned = sum(a.score for a in attempts)
            total_possible = sum(a.total_questions for a in attempts)
            if total_possible > 0:
                avg_score = round((total_earned / total_possible) * 100, 1)

        performance_data.append({
            "topic": doc.title,
            "quiz_attempts": total_attempts,
            "average_score": avg_score
        })

    # Convert to string for the prompt
    context_str = json.dumps(performance_data, indent=2)

    # 2. Build the Prompt
    prompt = f"""
    You are an AI personal tutor analyzing a student's recent performance data.
    Based on the following data about the topics they are studying and their quiz scores:

    {context_str}

    Identify their biggest knowledge gap (the topic they struggle with most or have the lowest score in, or just pick one if scores are similar).
    Suggest a tutoring style that would help them most.
    Recommend specific concepts to review based on the topic.
    Provide a 3-step spaced repetition schedule (Today, Tomorrow, After 2 days).

    Return ONLY a valid JSON object matching this exact structure, with no markdown formatting or extra text outside the JSON:
    {{
      "knowledge_gap": "The name of the weakest topic or concept",
      "suggested_tutor_style": "Brief suggestion (e.g., 'Beginner explanation', 'Socratic method')",
      "recommended_content": "A comma-separated list of specific concepts to study",
      "spaced_repetition_schedule": {{
        "today": "What to do today",
        "tomorrow": "What to do tomorrow",
        "after_2_days": "What to do after 2 days"
      }}
    }}
    """

    # 3. Call Gemini
    response = generate_response(prompt)
    if not response:
        return None

    # 4. Parse JSON
    try:
        # Clean up any surrounding markdown code blocks if the model ignored the instruction
        cleaned_response = re.sub(r"```json", "", response)
        cleaned_response = re.sub(r"```", "", cleaned_response).strip()
        
        plan_data = json.loads(cleaned_response)
        return plan_data
    except Exception as e:
        print(f"Error parsing revision plan JSON: {e}")
        print(f"Raw Response: {response}")
        return None
