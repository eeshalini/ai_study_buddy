from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, F
from django.db import models
from .models import StudyDocument, ChatMessage, FlashCard, QuizQuestion, QuizAttempt, MindMap
from .services.document_processor import extract_text
from .services.index_manager import build_and_save_index
from .services.rag_engine import generate_rag_answer
from .services.flashcard_engine import generate_flashcards
from .services.quiz_engine import generate_quiz
from .services.mindmap_engine import generate_mindmap
from .services.revision_engine import generate_revision_plan
from .models import RevisionPlan

@login_required
def dashboard(request):
    documents = StudyDocument.objects.filter(user=request.user).exclude(file="").exclude(file__isnull=True)
    return render(request, "learning/dashboard.html", {
        "documents": documents
    })


@login_required
def upload_document(request):
    if request.method == "POST":
        file = request.FILES.get("file")
        title = request.POST.get("title")

        if file:
            doc = StudyDocument.objects.create(
                user=request.user, title=title, file=file
            )

            file_path = doc.file.path

            text = extract_text(file_path)

            build_and_save_index(request.user.id, doc.id, text)

            return redirect("dashboard")
    return render(request, "learning/upload.html")


@login_required
def new_chat(request):
    doc = StudyDocument.objects.create(
        user=request.user, title="New General Chat", file=""
    )
    return redirect("chat", doc_id=doc.id)


@login_required
def chat_view(request, doc_id):
    document = StudyDocument.objects.get(id=doc_id, user=request.user)
    messages = ChatMessage.objects.filter(
        user=request.user,
        document=document
    ).order_by("created_at")

    # Filter user_documents to only show:
    # 1. Documents with at least one message
    # 2. Documents that are general chats (no file)
    user_documents = StudyDocument.objects.filter(
        user=request.user
    ).annotate(
        num_messages=models.Count('chatmessage')
    ).filter(
        models.Q(num_messages__gt=0) | models.Q(file='') | models.Q(file__isnull=True)
    ).order_by("-uploaded_at")


    if request.method == "POST":
        query = request.POST.get("question")

        answer = generate_rag_answer(
            request.user.id,
            document.id,
            query
        )

        ChatMessage.objects.create(
            user=request.user,
            document=document,
            question=query,
            answer=answer
        )

        return redirect("chat", doc_id=doc_id)

    return render(request, "learning/chat.html", {
        "messages": messages,
        "document": document,
        "user_documents": user_documents
    })



@login_required
def generate_flashcards_view(request, doc_id):
    document = StudyDocument.objects.get(id=doc_id, user=request.user)

    cards = generate_flashcards(request.user.id, document.id)

    if not cards:
        messages.error(request, "Failed to generate flashcards. You may have exceeded the AI rate limit.")
        return redirect("flashcards", doc_id=doc_id)

    FlashCard.objects.filter(user=request.user, document=document).delete()

    for card in cards:
        FlashCard.objects.create(
            user=request.user,
            document=document,
            question=card["question"],
            answer=card["answer"]
        )

    return redirect("flashcards", doc_id=doc_id)


@login_required
def flashcards_view(request, doc_id):
    document = StudyDocument.objects.get(id=doc_id, user=request.user)

    cards = FlashCard.objects.filter(
        user=request.user,
        document=document
    )

    return render(request, "learning/flashcards.html", {
        "cards": cards,
        "document": document
    })



@login_required
def generate_quiz_view(request, doc_id):
    document = StudyDocument.objects.get(id=doc_id, user=request.user)

    num_questions = 5
    if request.method == "POST":
        try:
            num_questions = int(request.POST.get("num_questions", 5))
        except ValueError:
            num_questions = 5

    questions = generate_quiz(request.user.id, document.id, num_questions=num_questions)

    if not questions:
        messages.error(request, "Failed to generate quiz. You may have exceeded the AI rate limit.")
        return redirect("quiz", doc_id=doc_id)

    QuizQuestion.objects.filter(user=request.user, document=document).delete()

    for q in questions:
        QuizQuestion.objects.create(
            user=request.user,
            document=document,
            question=q["question"],
            option_a=q["A"],
            option_b=q["B"],
            option_c=q["C"],
            option_d=q["D"],
            correct_answer=q["correct"]
        )

    return redirect("quiz", doc_id=doc_id)


@login_required
def quiz_view(request, doc_id):
    document = StudyDocument.objects.get(id=doc_id, user=request.user)

    questions = QuizQuestion.objects.filter(
        user=request.user,
        document=document
    )

    return render(request, "learning/quiz.html", {
        "questions": questions,
        "document": document
    })


@login_required
def submit_quiz_view(request, doc_id):
    document = StudyDocument.objects.get(id=doc_id, user=request.user)

    questions = QuizQuestion.objects.filter(
        user=request.user,
        document=document
    )
    
    

    score = 0

    for q in questions:
        selected = request.POST.get(str(q.id))
        if selected == q.correct_answer:
            score += 1

    QuizAttempt.objects.create(
        user=request.user,
        document=document,
        score=score,
        total_questions=questions.count()
    )

    return render(request, "learning/quiz_result.html", {
        "score": score,
        "total": questions.count(),
        "document": document
    })


@login_required
def generate_mindmap_view(request, doc_id):
    document = StudyDocument.objects.get(id=doc_id, user=request.user)
    
    map_type = request.GET.get('type', 'overview')

    content = generate_mindmap(request.user.id, document.id, map_type)
    print(content)
    if content:
        MindMap.objects.filter(user=request.user, document=document, map_type=map_type).delete()

        MindMap.objects.create(
            user=request.user,
            document=document,
            content=content,
            map_type=map_type
        )
    else:
        messages.error(request, "Failed to generate mindmap. You may have exceeded the AI rate limit.")

    return redirect(f"/learning/mindmap/{doc_id}/?type={map_type}")


@login_required
def mindmap_view(request, doc_id):
    document = StudyDocument.objects.get(id=doc_id, user=request.user)
    
    map_type = request.GET.get('type', 'overview')

    mindmap = MindMap.objects.filter(
        user=request.user,
        document=document,
        map_type=map_type
    ).first()

    return render(request, "learning/mindmap.html", {
        "document": document,
        "mindmap": mindmap,
        "current_type": map_type
    })


@login_required
def analytics_view(request):
    documents = StudyDocument.objects.filter(user=request.user)

    doc_data = []

    for doc in documents:
        doc_attempts = QuizAttempt.objects.filter(user=request.user, document=doc)
        total_quizzes = doc_attempts.count()
        avg_score = doc_attempts.aggregate(avg=Avg('score'))['avg']
        
        # Calculate percentage for display
        avg_score_val = 0
        if total_quizzes > 0 and avg_score is not None:
            # Assuming max score is usually 5 questions for now based on generic quiz size, 
            # ideally we'd use total_questions but avg aggregates make it complex.
            # We'll use a direct percentage if we just calculate it in python:
            total_earned = sum(a.score for a in doc_attempts)
            total_possible = sum(a.total_questions for a in doc_attempts)
            if total_possible > 0:
                avg_score_val = round((total_earned / total_possible) * 100, 1)

        total_flashcards = FlashCard.objects.filter(user=request.user, document=doc).count()
        total_chat_messages = ChatMessage.objects.filter(user=request.user, document=doc).count()

        # We don't have question-specific tracking yet, but we can flag attempts < 60% as "Needs Review"
        weak_topics = []
        low_score_attempts = doc_attempts.filter(score__lt=models.F('total_questions') * 0.6)
        if low_score_attempts.exists():
            weak_topics.append({
                "topic": f"{doc.title} Core Concepts",
                "accuracy": round(sum(a.score for a in low_score_attempts) / sum(a.total_questions for a in low_score_attempts) * 100, 1) if sum(a.total_questions for a in low_score_attempts) > 0 else 0
            })

        doc_data.append({
            "document": doc,
            "total_quizzes": total_quizzes,
            "avg_score": avg_score_val,
            "total_flashcards": total_flashcards,
            "total_chat_messages": total_chat_messages,
            "weak_topics": weak_topics
        })

    # Overall user stats
    all_attempts = QuizAttempt.objects.filter(user=request.user)
    overall_total_quizzes = all_attempts.count()
    overall_earned = sum(a.score for a in all_attempts)
    overall_possible = sum(a.total_questions for a in all_attempts)
    overall_avg = round((overall_earned / overall_possible) * 100, 1) if overall_possible > 0 else 0

    revision_plan = RevisionPlan.objects.filter(user=request.user).first()

    return render(request, "learning/analytics.html", {
        "doc_data": doc_data,
        "data": {
            "total_quizzes": overall_total_quizzes,
            "avg_score": overall_avg
        },
        "revision_plan": revision_plan.plan_data if revision_plan else None,
        "revision_plan_date": revision_plan.created_at if revision_plan else None,
    })

@login_required
def generate_revision_plan_view(request):
    plan_data = generate_revision_plan(request.user.id)
    if plan_data:
        # Initialize completion states
        plan_data.setdefault('completed', {'today': False, 'tomorrow': False, 'after_2_days': False})
        RevisionPlan.objects.update_or_create(
            user=request.user,
            defaults={"plan_data": plan_data}
        )
    else:
        messages.error(request, "Failed to generate revision plan. You may have exceeded the AI rate limit.")
    return redirect("analytics")

from django.http import JsonResponse
import json

@login_required
def toggle_revision_task(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            day = data.get('day')
            if day not in ['today', 'tomorrow', 'after_2_days']:
                return JsonResponse({"error": "Invalid day"}, status=400)
                
            revision_plan = RevisionPlan.objects.filter(user=request.user).first()
            if not revision_plan:
                return JsonResponse({"error": "No plan exists"}, status=404)
                
            plan_data = revision_plan.plan_data
            if 'completed' not in plan_data:
                plan_data['completed'] = {'today': False, 'tomorrow': False, 'after_2_days': False}
                
            # Toggle the boolean
            plan_data['completed'][day] = not plan_data['completed'][day]
            
            revision_plan.plan_data = plan_data
            revision_plan.save()
            
            return JsonResponse({"success": True, "state": plan_data['completed'][day]})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid method"}, status=405)

@login_required
def delete_document(request, doc_id):
    if request.method == "POST":
        document = StudyDocument.objects.get(id=doc_id, user=request.user)
        document.delete()
        
        # Check if the user was on the chat page of the deleted document
        # by checking the HTTP_REFERER, or just unconditionally redirect to the latest doc
        # if they have any remaining docs.
        latest_doc = StudyDocument.objects.filter(user=request.user).order_by("-uploaded_at").first()
        if latest_doc:
            return redirect("chat", doc_id=latest_doc.id)
            
    return redirect("dashboard")

@login_required
def clear_history(request, doc_id):
    if request.method == "POST":
        document = StudyDocument.objects.get(id=doc_id, user=request.user)
        
        # Clear chat history (messages)
        ChatMessage.objects.filter(user=request.user, document=document).delete()
        
        # If it's a general chat (no file), delete the document itself
        if not document.file:
            document.delete()
            return redirect("dashboard")
            
        # For uploaded documents, we just cleared the history.
        # The sidebar filtering will now hide it from the chat interface.
        messages.success(request, "Chat history cleared.")
        
    return redirect("dashboard")
