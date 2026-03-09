from django.urls import path
from . import views
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("upload/", views.upload_document, name="upload_document"),
    path("new-chat/", views.new_chat, name="new_chat"),
    path("chat/<int:doc_id>/", views.chat_view, name="chat"),
    path("flashcards/<int:doc_id>/", views.flashcards_view, name="flashcards"),
    path(
        "generate-flashcards/<int:doc_id>/",
        views.generate_flashcards_view,
        name="generate_flashcards",
    ),
    path("quiz/<int:doc_id>/", views.quiz_view, name="quiz"),
    path("generate-quiz/<int:doc_id>/", views.generate_quiz_view, name="generate_quiz"),
    path("submit-quiz/<int:doc_id>/", views.submit_quiz_view, name="submit_quiz"),
    path("mindmap/<int:doc_id>/", views.mindmap_view, name="mindmap"),
    path(
        "generate-mindmap/<int:doc_id>/",
        views.generate_mindmap_view,
        name="generate_mindmap",
    ),
    path('analytics/', views.analytics_view, name='analytics'),
    path('analytics/generate-revision-plan/', views.generate_revision_plan_view, name='generate_revision_plan'),
    path('analytics/toggle-revision-task/', views.toggle_revision_task, name='toggle_revision_task'),
    path('delete/<int:doc_id>/', views.delete_document, name='delete_document'),
    path('clear-history/<int:doc_id>/', views.clear_history, name='clear_history'),
]

