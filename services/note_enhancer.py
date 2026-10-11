import os
from services.sarvam_client import get_sarvam_client

def generate_lecture_notes(transcript: str, topic_hint: str = "") -> str:
    """
    Transforms raw lecture transcript (including code-mixed Hinglish/regional speech)
    into clean, structured, textbook-quality revision notes using Sarvam-105B.
    """
    client = get_sarvam_client()

    system_prompt = (
        "You are an expert academic tutor and notes creator. "
        "Transform raw lecture transcripts into well-structured, comprehensive revision notes. "
        "Remove filler words, repetitions, and spoken disfluencies. "
        "If the lecture was in Hinglish or mixed languages, translate and standardize into clear, fluent English "
        "(or keep key Indic terms where appropriate). "
        "Format the notes with:\n"
        "1. # Title & Executive Summary\n"
        "2. ## Core Concepts & Explanations (with bullet points and bold keywords)\n"
        "3. ## Key Definitions & Mathematical Formulas (use LaTeX formatting with $ and $$)\n"
        "4. ## Examples & Practical Applications\n"
        "5. ## Important Takeaways & Quick Review Points\n"
        "Use GitHub Flavored Markdown with clean headers and tables where suitable."
    )

    user_content = f"Topic/Subject: {topic_hint}\n\nLecture Transcript:\n{transcript}" if topic_hint else f"Lecture Transcript:\n{transcript}"

    response = client.chat.completions(
        model="sarvam-105b-conversations",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content


def enhance_handwritten_notes(raw_ocr_markdown: str, topic_hint: str = "") -> str:
    """
    Takes raw OCR text extracted from handwritten notebooks and transforms it into
    a polished, comprehensive study guide with corrected equations, full explanations,
    and clear formatting.
    """
    client = get_sarvam_client()

    system_prompt = (
        "You are an expert academic editor specializing in student handwritten notes. "
        "Students often write in shorthand, incomplete sentences, or rough drawings. "
        "Your task is to take this raw OCR scan from handwritten notes and elevate it:\n"
        "1. Fix any OCR transcription errors, broken sentences, and cryptic abbreviations.\n"
        "2. Format all mathematical and scientific expressions cleanly using LaTeX ($...$ or $$...$$).\n"
        "3. Expand rough shorthand bullet points into complete, lucid conceptual explanations.\n"
        "4. Organize with hierarchical headings, highlight key terms, and add helpful summary tables.\n"
        "5. Add a 'Key Points to Memorize' section at the end."
    )

    user_content = f"Context/Subject: {topic_hint}\n\nScanned Handwritten Notes:\n{raw_ocr_markdown}" if topic_hint else f"Scanned Handwritten Notes:\n{raw_ocr_markdown}"

    response = client.chat.completions(
        model="sarvam-105b-conversations",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content


def merge_lecture_and_handwritten_notes(transcript: str, handwritten_notes: str, topic_hint: str = "") -> str:
    """
    Merges audio lecture transcript with student handwritten notes to produce
    a unified Master Study Guide.
    """
    client = get_sarvam_client()

    system_prompt = (
        "You are an elite academic educator. You have been given two complementary sources:\n"
        "1. What the professor said during the lecture (Lecture Transcript)\n"
        "2. What the student jotted down in their notebook (Handwritten Notes)\n\n"
        "Synthesize both sources into a unified, definitive Master Study Guide. "
        "Cross-reference student notes with the lecture context to explain everything with maximum clarity. "
        "Use clean Markdown formatting, LaTeX for math, bullet points, and high-yield study callouts."
    )

    user_content = (
        f"Topic: {topic_hint}\n\n"
        f"--- LECTURE TRANSCRIPT ---\n{transcript}\n\n"
        f"--- HANDWRITTEN NOTES ---\n{handwritten_notes}"
    )

    response = client.chat.completions(
        model="sarvam-105b-conversations",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content
