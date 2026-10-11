import streamlit as st
import os
import json
from dotenv import load_dotenv

# Load environment
load_dotenv()

from services.audio_transcriber import transcribe_audio
from services.document_scanner import digitise_handwritten_document
from services.note_enhancer import (
    generate_lecture_notes,
    enhance_handwritten_notes,
    merge_lecture_and_handwritten_notes,
)
from services.assessment_generator import (
    generate_quiz,
    generate_practice_test,
    generate_qa_flashcards,
)

# Page configuration
st.set_page_config(
    page_title="Sarvam StudyGenius | Lecture to Notes & Exam Prep",
    page_icon="🎓",
    layout="wide",
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.3rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .badge-card {
        padding: 0.8rem;
        border-radius: 8px;
        background-color: #F3F4F6;
        border-left: 4px solid #2563EB;
        margin-bottom: 1rem;
    }
    .score-badge {
        font-size: 1.5rem;
        font-weight: bold;
        color: #059669;
        padding: 0.5rem 1rem;
        background-color: #D1FAE5;
        border-radius: 8px;
        display: inline-block;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "active_notes" not in st.session_state:
    st.session_state.active_notes = ""
if "lecture_transcript" not in st.session_state:
    st.session_state.lecture_transcript = ""
if "lecture_notes" not in st.session_state:
    st.session_state.lecture_notes = ""
if "scanned_raw_notes" not in st.session_state:
    st.session_state.scanned_raw_notes = ""
if "scanned_polished_notes" not in st.session_state:
    st.session_state.scanned_polished_notes = ""
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = []
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "exam_paper" not in st.session_state:
    st.session_state.exam_paper = ""
if "flashcards" not in st.session_state:
    st.session_state.flashcards = []

# Sidebar
with st.sidebar:
    st.title("⚙️ Sarvam AI Suite")
    api_key = os.environ.get("SARVAM_API_KEY", "")
    if api_key:
        st.success("✅ Sarvam API Key Active")
    else:
        st.error("⚠️ SARVAM_API_KEY not found in .env")

    st.markdown("---")
    st.markdown("### 🤖 Powered By")
    st.markdown("- **Saaras v3**: Speech-to-Text (Indic & Hinglish)")
    st.markdown("- **Sarvam Vision**: Handwritten Doc AI OCR")
    st.markdown("- **Sarvam-105B**: 105B Indic LLM for Notes & Quizzes")

    st.markdown("---")
    st.markdown("### 💡 Quick Tip")
    st.info(
        "Upload a lecture or scan your notebook. You can seamlessly send generated notes "
        "to the Quiz Arena with one click to test your mastery!"
    )

# Header
st.markdown('<div class="main-header">🎓 Sarvam StudyGenius</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">AI-Powered Lecture-to-Notes, Handwritten Note Enhancer, and Automated Quiz & Test Prep</div>',
    unsafe_allow_html=True,
)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🎙️ 1. Lecture to Notes",
    "✍️ 2. Scan Handwritten Notes",
    "🔄 3. Merge & Master Guide",
    "🧠 4. Quizzes & Tests",
])

# -------------------------------------------------------------
# TAB 1: Lecture to Notes
# -------------------------------------------------------------
with tab1:
    st.header("Transform Lecture Audio into Structured Notes")
    st.write(
        "Upload audio recordings of your lectures (supports English, Hindi, Tamil, Telugu, and mixed classroom speech like Hinglish)."
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        audio_file = st.file_uploader(
            "Upload Lecture Audio (.mp3, .wav, .m4a, .ogg)",
            type=["mp3", "wav", "m4a", "ogg"],
            key="audio_uploader",
        )
        col_lang, col_mode = st.columns(2)
        with col_lang:
            lang_choice = st.selectbox(
                "Spoken Language",
                options=["unknown", "en-IN", "hi-IN", "ta-IN", "te-IN", "bn-IN", "mr-IN"],
                format_func=lambda x: {
                    "unknown": "Auto Detect",
                    "en-IN": "English (Indian)",
                    "hi-IN": "Hindi / Hinglish",
                    "ta-IN": "Tamil",
                    "te-IN": "Telugu",
                    "bn-IN": "Bengali",
                    "mr-IN": "Marathi",
                }.get(x, x),
            )
        with col_mode:
            stt_mode = st.selectbox(
                "Transcription Mode",
                options=["codemix", "transcribe", "verbatim"],
                help="'codemix' is recommended for multilingual / Hinglish classrooms.",
            )

        lecture_topic = st.text_input(
            "Subject / Topic Hint (Optional)",
            placeholder="e.g. Thermodynamics Lecture 3, Operating Systems",
        )

        manual_transcript = st.text_area(
            "Or Paste Existing Transcript Directly",
            placeholder="If you already have lecture text, paste it here to skip audio transcription...",
            height=120,
        )

        process_lecture_btn = st.button("🚀 Process & Generate Notes", key="lecture_btn", type="primary")

    with col2:
        if process_lecture_btn:
            transcript = ""
            if audio_file:
                with st.spinner("🎙️ Transcribing audio with Sarvam Saaras v3..."):
                    try:
                        res = transcribe_audio(
                            audio_file=audio_file,
                            filename=audio_file.name,
                            language_code=lang_choice,
                            mode=stt_mode,
                        )
                        transcript = res.get("transcript", "")
                        st.session_state.lecture_transcript = transcript
                        st.success("✅ Audio Transcribed Successfully!")
                    except Exception as e:
                        st.error(f"Error during audio transcription: {e}")
            elif manual_transcript.strip():
                transcript = manual_transcript.strip()
                st.session_state.lecture_transcript = transcript
            else:
                st.warning("Please upload an audio file or paste transcript text.")

            if transcript:
                with st.spinner("✍️ Generating textbook-quality revision notes with Sarvam-105B..."):
                    try:
                        notes = generate_lecture_notes(transcript, topic_hint=lecture_topic)
                        st.session_state.lecture_notes = notes
                        st.session_state.active_notes = notes
                        st.success("✅ Structured Notes Generated!")
                    except Exception as e:
                        st.error(f"Error generating notes: {e}")

        if st.session_state.lecture_notes:
            st.subheader("📖 Generated Revision Notes")
            with st.expander("🔍 View Raw Transcript", expanded=False):
                st.write(st.session_state.lecture_transcript)

            st.markdown(st.session_state.lecture_notes)

            c_down, c_send = st.columns([1, 1])
            with c_down:
                st.download_button(
                    "📥 Download Notes (.md)",
                    data=st.session_state.lecture_notes,
                    file_name="lecture_notes.md",
                    mime="text/markdown",
                )
            with c_send:
                if st.button("➡️ Send to Quiz Arena", key="send_lecture_quiz"):
                    st.session_state.active_notes = st.session_state.lecture_notes
                    st.success("Notes loaded into Quiz Arena! Switch to Tab 4.")

# -------------------------------------------------------------
# TAB 2: Scan Handwritten Notes
# -------------------------------------------------------------
with tab2:
    st.header("Scan Handwritten Notebooks & Enhance Them")
    st.write(
        "Upload a photo or PDF of your handwritten classroom notes. "
        "Sarvam Vision extracts text and diagrams, and Sarvam-105B expands shorthand into clear explanations."
    )

    col_h1, col_h2 = st.columns([1, 1])

    with col_h1:
        doc_file = st.file_uploader(
            "Upload Handwritten Notes Photo or PDF (.png, .jpg, .pdf)",
            type=["png", "jpg", "jpeg", "pdf"],
            key="doc_uploader",
        )
        if doc_file and doc_file.type.startswith("image/"):
            st.image(doc_file, caption="Uploaded Notes Preview", use_container_width=True)

        col_dlang, col_dtype = st.columns(2)
        with col_dlang:
            doc_lang = st.selectbox(
                "Document Language",
                options=["en-IN", "hi-IN", "ta-IN", "te-IN", "bn-IN"],
                format_func=lambda x: {
                    "en-IN": "English",
                    "hi-IN": "Hindi",
                    "ta-IN": "Tamil",
                    "te-IN": "Telugu",
                    "bn-IN": "Bengali",
                }.get(x, x),
                key="doc_lang_select",
            )
        with col_dtype:
            content_type = st.selectbox(
                "Content Type",
                options=["handwritten", "mixed", "printed"],
                index=0,
            )

        handwritten_topic = st.text_input(
            "Subject / Topic Hint",
            placeholder="e.g. Calculus Derivatives, Organic Chemistry",
            key="hw_topic",
        )

        scan_btn = st.button("🔍 Scan & Enhance Notes", key="scan_btn", type="primary")

    with col_h2:
        if scan_btn:
            if doc_file:
                with st.spinner("📷 Scanning handwritten document with Sarvam Vision (Doc AI)..."):
                    try:
                        scan_res = digitise_handwritten_document(
                            doc_file=doc_file,
                            filename=doc_file.name,
                            language=doc_lang,
                            content_type=content_type,
                        )
                        st.session_state.scanned_raw_notes = scan_res.get("markdown_text", "")
                        st.success(f"✅ Digitisation Complete! (Status: {scan_res.get('status')})")
                    except Exception as e:
                        st.error(f"Error during OCR scan: {e}")

                if st.session_state.scanned_raw_notes:
                    with st.spinner("✨ Polishing shorthand, equations, and structure with Sarvam-105B..."):
                        try:
                            enhanced = enhance_handwritten_notes(
                                st.session_state.scanned_raw_notes,
                                topic_hint=handwritten_topic,
                            )
                            st.session_state.scanned_polished_notes = enhanced
                            st.session_state.active_notes = enhanced
                            st.success("✅ Notes Enhanced & Cleaned Up!")
                        except Exception as e:
                            st.error(f"Error enhancing notes: {e}")
            else:
                st.warning("Please upload a handwritten note image or PDF.")

        if st.session_state.scanned_polished_notes:
            st.subheader("✨ Polished & Formatted Study Guide")
            with st.expander("📄 View Raw Digitized OCR Text", expanded=False):
                st.write(st.session_state.scanned_raw_notes)

            st.markdown(st.session_state.scanned_polished_notes)

            c_down2, c_send2 = st.columns([1, 1])
            with c_down2:
                st.download_button(
                    "📥 Download Polished Notes (.md)",
                    data=st.session_state.scanned_polished_notes,
                    file_name="polished_handwritten_notes.md",
                    mime="text/markdown",
                )
            with c_send2:
                if st.button("➡️ Send to Quiz Arena", key="send_hw_quiz"):
                    st.session_state.active_notes = st.session_state.scanned_polished_notes
                    st.success("Notes loaded into Quiz Arena! Switch to Tab 4.")

# -------------------------------------------------------------
# TAB 3: Merge & Master Guide
# -------------------------------------------------------------
with tab3:
    st.header("Merge Lecture Audio + Handwritten Notes")
    st.write(
        "Synthesize what the professor spoke with what you wrote into a comprehensive Master Study Guide."
    )

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        txt1 = st.text_area(
            "Lecture Transcript / Notes",
            value=st.session_state.lecture_transcript or st.session_state.lecture_notes,
            height=200,
            placeholder="Paste or import lecture transcript...",
        )
    with col_m2:
        txt2 = st.text_area(
            "Handwritten Notes",
            value=st.session_state.scanned_raw_notes or st.session_state.scanned_polished_notes,
            height=200,
            placeholder="Paste or import handwritten notes...",
        )

    merge_topic = st.text_input("Master Guide Topic Name", placeholder="e.g. Computer Networks - OSI Model")
    if st.button("🔮 Generate Master Study Guide", key="merge_btn", type="primary"):
        if txt1 and txt2:
            with st.spinner("Synthesizing lecture audio with handwritten notes via Sarvam-105B..."):
                try:
                    master_notes = merge_lecture_and_handwritten_notes(txt1, txt2, topic_hint=merge_topic)
                    st.session_state.active_notes = master_notes
                    st.subheader("📚 Master Study Guide")
                    st.markdown(master_notes)
                    st.download_button(
                        "📥 Download Master Guide (.md)",
                        data=master_notes,
                        file_name="master_study_guide.md",
                        mime="text/markdown",
                    )
                except Exception as e:
                    st.error(f"Error merging notes: {e}")
        else:
            st.warning("Please provide both lecture and handwritten content.")

# -------------------------------------------------------------
# TAB 4: Quizzes & Tests Arena
# -------------------------------------------------------------
with tab4:
    st.header("🧠 Automated Quiz, Exam & Flashcards Generator")
    st.write(
        "Generate assessment questions, interactive multiple-choice quizzes, or full mock exam papers "
        "directly from your lecture and notes."
    )

    study_material = st.text_area(
        "Study Notes Source Material for Test Generation",
        value=st.session_state.active_notes,
        height=180,
        placeholder="Notes content from previous tabs will appear here, or you can paste any custom notes...",
    )

    assessment_type = st.radio(
        "Select Assessment Format:",
        options=["Interactive Multiple Choice Quiz (MCQs)", "Full Practice Examination Paper", "Active Recall Flashcards"],
        horizontal=True,
    )

    if assessment_type == "Interactive Multiple Choice Quiz (MCQs)":
        col_q1, col_q2 = st.columns(2)
        with col_q1:
            num_q = st.slider("Number of Questions", min_value=3, max_value=10, value=5)
        with col_q2:
            diff = st.selectbox("Difficulty Level", ["Easy", "Medium", "Challenging", "Olympiad / Exam Level"])

        if st.button("🎯 Generate MCQ Quiz", key="gen_mcq_btn", type="primary"):
            if not study_material.strip():
                st.warning("Please provide study notes above.")
            else:
                with st.spinner("Generating conceptual quiz with Sarvam-105B..."):
                    try:
                        quiz_list = generate_quiz(study_material, num_questions=num_q, difficulty=diff)
                        st.session_state.quiz_data = quiz_list
                        st.session_state.quiz_submitted = False
                        st.session_state.user_answers = {}
                        st.success(f"Generated {len(quiz_list)} questions!")
                    except Exception as e:
                        st.error(f"Error generating quiz: {e}")

        # Render Interactive Quiz
        if st.session_state.quiz_data:
            st.markdown("---")
            st.subheader("📝 Interactive Quiz")

            with st.form("quiz_form"):
                for idx, q_item in enumerate(st.session_state.quiz_data):
                    q_id = q_item.get("id", idx + 1)
                    q_text = q_item.get("question", "")
                    options = q_item.get("options", [])

                    st.markdown(f"**Q{idx + 1}: {q_text}**")
                    selected = st.radio(
                        f"Choose answer for Q{idx + 1}:",
                        options=options,
                        key=f"q_{idx}",
                        label_visibility="collapsed",
                    )
                    st.session_state.user_answers[idx] = selected
                    st.markdown("")

                submit_quiz = st.form_submit_button("🏁 Submit Answers & Check Score")

            if submit_quiz:
                st.session_state.quiz_submitted = True

            if st.session_state.quiz_submitted:
                correct_count = 0
                total_count = len(st.session_state.quiz_data)

                st.markdown("### 📊 Quiz Results & Feedback")
                for idx, q_item in enumerate(st.session_state.quiz_data):
                    user_ans = st.session_state.user_answers.get(idx, "")
                    correct_ans_letter = str(q_item.get("correct_answer", "")).strip().upper()
                    # Clean answer letter from options e.g. "A) ..." -> "A"
                    user_letter = user_ans[:1].upper() if user_ans else ""

                    is_correct = (user_letter == correct_ans_letter)
                    if is_correct:
                        correct_count += 1
                        st.success(f"**Q{idx + 1}: Correct!** You selected: `{user_ans}`")
                    else:
                        st.error(f"**Q{idx + 1}: Incorrect!** You selected: `{user_ans}`. Correct answer: **Option {correct_ans_letter}**")

                    st.info(f"💡 **Explanation:** {q_item.get('explanation', 'N/A')}")
                    st.markdown("---")

                percentage = (correct_count / total_count) * 100 if total_count > 0 else 0
                st.markdown(
                    f'<div class="score-badge">Final Score: {correct_count}/{total_count} ({percentage:.1f}%)</div>',
                    unsafe_allow_html=True,
                )

    elif assessment_type == "Full Practice Examination Paper":
        exam_title = st.text_input("Exam Title", value="Comprehensive Mastery Examination")
        if st.button("📋 Generate Full Practice Exam", key="gen_exam_btn", type="primary"):
            if not study_material.strip():
                st.warning("Please provide study notes above.")
            else:
                with st.spinner("Drafting full mock test paper & marking rubric with Sarvam-105B..."):
                    try:
                        exam_md = generate_practice_test(study_material, test_title=exam_title)
                        st.session_state.exam_paper = exam_md
                        st.success("Exam Paper Generated Successfully!")
                    except Exception as e:
                        st.error(f"Error generating exam: {e}")

        if st.session_state.exam_paper:
            st.markdown("---")
            st.markdown(st.session_state.exam_paper)
            st.download_button(
                "📥 Download Exam Paper with Answer Key (.md)",
                data=st.session_state.exam_paper,
                file_name="practice_exam_paper.md",
                mime="text/markdown",
            )

    elif assessment_type == "Active Recall Flashcards":
        card_count = st.slider("Number of Flashcards", min_value=4, max_value=12, value=6)
        if st.button("🗂️ Generate Flashcards", key="gen_cards_btn", type="primary"):
            if not study_material.strip():
                st.warning("Please provide study notes above.")
            else:
                with st.spinner("Generating active-recall cards with Sarvam-105B..."):
                    try:
                        cards = generate_qa_flashcards(study_material, count=card_count)
                        st.session_state.flashcards = cards
                        st.success(f"Generated {len(cards)} flashcards!")
                    except Exception as e:
                        st.error(f"Error generating flashcards: {e}")

        if st.session_state.flashcards:
            st.markdown("---")
            st.subheader("🗂️ Flashcards (Click to reveal answer)")
            for i, card in enumerate(st.session_state.flashcards):
                with st.expander(f"📌 Card {i+1}: {card.get('question', '')}"):
                    st.write(card.get("answer", ""))
