"""
RepoMind — LLM integration via Google Gemini API.
"""

import google.generativeai as genai

from config import GOOGLE_API_KEY, GEMINI_MODEL

# Configure the Gemini client
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

SYSTEM_PROMPT = """\
You are RepoMind, an expert senior software engineer.  A user is asking \
questions about a GitHub repository's codebase. You have been given relevant \
code snippets retrieved from the repository.

Your job is to:
1. Analyze the provided code snippets carefully.
2. Answer the user's question accurately and concisely.
3. Reference specific files and functions when relevant.
4. If the snippets don't contain enough information, say so honestly.
5. Format your response using Markdown — use code blocks, bold text, \
   bullet points, and headings where appropriate.
6. When explaining architecture, describe the relationships between \
   components clearly.
"""


def ask_llm(question: str, context_snippets: list[dict]) -> str:
    """
    Send a question along with retrieved code snippets to Google Gemini.

    Args:
        question: The user's natural-language question.
        context_snippets: List of dicts with "text" and "file_path".

    Returns:
        The AI-generated answer string.
    """
    if not GOOGLE_API_KEY:
        return (
            "⚠️ **Google API key not configured.**\n\n"
            "Please set `GOOGLE_API_KEY` in your `.env` file to enable AI answers."
        )

    # Build the context block
    context_parts: list[str] = []
    for i, snippet in enumerate(context_snippets, 1):
        file_info = f"  (from `{snippet['file_path']}`)" if snippet.get("file_path") else ""
        context_parts.append(
            f"### Snippet {i}{file_info}\n```\n{snippet['text']}\n```"
        )

    context_block = "\n\n".join(context_parts)

    user_prompt = (
        f"## Retrieved Code Snippets\n\n{context_block}\n\n"
        f"---\n\n## User's Question\n\n{question}"
    )

    try:
        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            system_instruction=SYSTEM_PROMPT,
        )
        response = model.generate_content(user_prompt)
        return response.text
    except Exception as exc:
        return f"❌ **Error from Gemini API:** {exc}"
