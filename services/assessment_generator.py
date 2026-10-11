import json
import re
from typing import List, Dict, Any
from services.sarvam_client import get_sarvam_client

def generate_quiz(
    notes_content: str,
    num_questions: int = 5,
    difficulty: str = "Medium"
) -> List[Dict[str, Any]]:
    """
    Generates interactive multiple-choice questions (MCQs) based on notes content.
    Returns a list of dicts with question, options, correct_answer, and explanation.
    """
    client = get_sarvam_client()

    prompt = f"""You are a master educator designing a high-yield assessment quiz.
Based strictly on the provided study notes, generate exactly {num_questions} Multiple Choice Questions (MCQs) at a {difficulty} difficulty level.

IMPORTANT: You MUST respond ONLY with a valid JSON array of objects. Do not include markdown formatting or commentary outside the JSON.
Each object must follow this exact schema:
[
  {{
    "id": 1,
    "question": "Question text here?",
    "options": [
      "A) First option",
      "B) Second option",
      "C) Third option",
      "D) Fourth option"
    ],
    "correct_answer": "A",
    "explanation": "Detailed explanation of why this answer is correct and why other options are incorrect."
  }}
]

Study Notes:
{notes_content[:4000]}
"""

    response = client.chat.completions(
        model="sarvam-105b-conversations",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content.strip()

    # Extract JSON array using regex if enclosed in code blocks
    match = re.search(r"\[\s*\{.*\}\s*\]", content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    # Fallback to direct json.loads
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # If model returned text, provide a fallback parsing or dummy format
        return [
            {
                "id": 1,
                "question": "Could not parse JSON quiz. Here is the raw generation:",
                "options": ["A) View in practice test tab", "B) Retry", "C) Edit notes", "D) Continue"],
                "correct_answer": "A",
                "explanation": content
            }
        ]


def generate_practice_test(
    notes_content: str,
    test_title: str = "Lecture & Notes Mastery Exam"
) -> str:
    """
    Generates a full formal practice test paper with questions and an answer key.
    """
    client = get_sarvam_client()

    prompt = f"""You are a university professor creating an official examination paper based on the following lecture and notes content.

Generate a comprehensive exam titled '{test_title}' with the following structure:
1. # {test_title}
   - Time Allowed & Total Marks
   - General Instructions
2. ## Section A: Quick Concept Checks (Short Answer / 2 Marks Each) - 5 Questions
3. ## Section B: Analytical & Application Problems (5 Marks Each) - 3 Questions
4. ## Section C: Deep-Dive Problem / Comprehensive Essay (10 Marks Each) - 2 Questions
5. ## 📝 Answer Key & Detailed Marking Rubric
   - Provide complete step-by-step solutions for every single question above.

Content to base the exam on:
{notes_content}
"""

    response = client.chat.completions(
        model="sarvam-105b-conversations",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content


def generate_qa_flashcards(notes_content: str, count: int = 6) -> List[Dict[str, str]]:
    """
    Generates active-recall flashcard pairs (Question & Concise Answer).
    """
    client = get_sarvam_client()

    prompt = f"""Generate exactly {count} high-yield active recall flashcards from these study notes.
Return ONLY a valid JSON array of objects with 'question' and 'answer' keys.

Schema:
[
  {{
    "question": "What is ...?",
    "answer": "Concise, precise explanation."
  }}
]

Study Notes:
{notes_content[:3500]}
"""

    response = client.chat.completions(
        model="sarvam-105b-conversations",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content.strip()
    match = re.search(r"\[\s*\{.*\}\s*\]", content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return [
            {"question": "Summary Question", "answer": content}
        ]
