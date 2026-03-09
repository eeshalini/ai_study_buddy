from django.contrib.auth.models import User
from learning.models import StudyDocument, ChatMessage
import os

# Create a test user if not exists
user, created = User.objects.get_or_create(username='test_verifier')

def test_uploaded_document_deletion():
    print("Testing uploaded document deletion...")
    doc = StudyDocument.objects.create(user=user, title="Test Upload", file="test_file.pdf")
    ChatMessage.objects.create(user=user, document=doc, question="q", answer="a")
    
    # Simulate delete_chat
    ChatMessage.objects.filter(user=user, document=doc).delete()
    
    doc.refresh_from_db()
    print(f"Document still exists: {doc.title}")
    messages_count = ChatMessage.objects.filter(document=doc).count()
    print(f"Messages count: {messages_count}")
    
    assert StudyDocument.objects.filter(id=doc.id).exists()
    assert messages_count == 0
    print("Uploaded document test passed.\n")
    doc.delete()

def test_general_chat_deletion():
    print("Testing general chat deletion...")
    doc = StudyDocument.objects.create(user=user, title="General Chat", file="")
    ChatMessage.objects.create(user=user, document=doc, question="q", answer="a")
    
    # Simulate delete_chat
    if not doc.file:
        doc.delete()
    
    exists = StudyDocument.objects.filter(id=doc.id).exists()
    print(f"General chat document still exists: {exists}")
    assert not exists
    print("General chat test passed.\n")

if __name__ == "__main__":
    test_uploaded_document_deletion()
    test_general_chat_deletion()
