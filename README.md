# AI Study Buddy 🚀

AI Study Buddy is a powerful, AI-driven learning platform built with Django and Google Gemini. It transforms your study materials (PDFs, PPTXs) into interactive learning tools, including RAG-powered chat, automated quizzes, mindmaps, and flashcards.

## ✨ Features

-   **RAG-Powered Chat**: Upload your documents and chat with them using Retrieval-Augmented Generation. Get precise answers based on your study material.
-   **Automated Quizzes**: Instantly generate multiple-choice quizzes from your documents to test your knowledge.
-   **Interactive Mindmaps**: Visualize complex concepts with AI-generated mindmaps (powered by Mermaid.js).
-   **Smart Flashcards**: Automatically create flashcards for active recall and better retention.
-   **Study Analytics**: Track your learning progress and get AI-generated revision plans.
-   **Premium UI/UX**: Modern, responsive interface with a beautiful **Dark Mode** toggle.

## 🛠️ Tech Stack

-   **Framework**: [Django 5.2+](https://www.djangoproject.com/)
-   **AI Engine**: [Google Gemini Pro/Flash](https://ai.google.dev/)
-   **Vector Database**: [FAISS](https://github.com/facebookresearch/faiss) (for RAG)
-   **Embeddings**: `sentence-transformers`
-   **Styling**: [Tailwind CSS](https://tailwindcss.com/)
-   **Database**: SQLite (Development)

## 🚀 Getting Started

### Prerequisites

-   Python 3.10+
-   A Google Gemini API Key (Get one from [Google AI Studio](https://aistudio.google.com/))

### Installation

1.  **Clone the repository**:
    ```bash
    git clone <your-repo-url>
    cd adaptive_rag
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv .venv
    # Windows:
    .venv\Scripts\activate
    # Linux/macOS:
    source .venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment**:
    Open `core/settings.py` and add your Gemini API Key:
    ```python
    GEMINI_API_KEY = "your_api_key_here"
    ```

5.  **Run Migrations**:
    ```bash
    python manage.py migrate
    ```

6.  **Start the Server**:
    ```bash
    python manage.py runserver
    ```

Visit `http://127.0.0.1:8000` to start learning!

## 📁 Project Structure

-   `accounts/`: User authentication and profile management.
-   `learning/`: Core logic for document processing, RAG, and study tools.
-   `learning/services/`: AI engines (Gemini client, Mindmap/Quiz/Flashcard engines).
-   `templates/`: UI components and page layouts.
-   `media/`: Storage for uploaded study materials.

## 📝 License

Distributed under the MIT License.
