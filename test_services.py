import sys
from services.sarvam_client import get_sarvam_client
from services.note_enhancer import generate_lecture_notes, enhance_handwritten_notes
from services.assessment_generator import generate_quiz, generate_qa_flashcards

def test_pipeline():
    print("1. Testing Sarvam client initialization...")
    client = get_sarvam_client()
    assert client is not None, "Client should not be None"
    print("   -> Sarvam client OK")

    sample_lecture = (
        "Today we discussed Newton's laws of motion. Specifically the second law, "
        "Force equals mass times acceleration, F = ma. We also talked about momentum p = mv, "
        "and how force is the rate of change of momentum dp/dt."
    )

    print("2. Testing Note Generation with Sarvam-105B...")
    notes = generate_lecture_notes(sample_lecture, topic_hint="Newtonian Mechanics")
    print("   -> Generated notes preview (first 100 chars):", notes[:100].replace("\n", " "))
    assert len(notes) > 50, "Notes should be generated"

    print("3. Testing Assessment Generator (Quiz MCQs)...")
    quiz = generate_quiz(notes, num_questions=2, difficulty="Easy")
    print(f"   -> Generated {len(quiz)} quiz questions")
    assert len(quiz) > 0, "Quiz should contain at least 1 question"
    assert "question" in quiz[0], "Quiz item should contain 'question'"

    print("4. Testing Assessment Generator (Flashcards)...")
    cards = generate_qa_flashcards(notes, count=2)
    print(f"   -> Generated {len(cards)} flashcards")
    assert len(cards) > 0, "Flashcards should contain at least 1 card"

    print("\nALL VERIFICATION CHECKS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_pipeline()
