# 🎓 Sarvam StudyGenius

> **AI-Powered Lecture-to-Notes, Handwritten Note Enhancer, and Automated Quiz & Test Prep** built with the [Sarvam AI Platform](https://sarvam.ai).

Sarvam StudyGenius is an intelligent study assistant tailored for Indian languages, English, and code-mixed classroom lectures (e.g. Hinglish). It bridges audio lectures and student notebooks into polished study guides and generates quizzes and formal mock exams.

---

## 🌟 Key Features

1. **🎙️ Lecture to Notes**:
   - Transcribes classroom audio recordings using **Saaras v3** (`client.speech_to_text.transcribe`).
   - Supports 22 Indian languages + English, with native handling of code-mixed classroom speech (`codemix` mode).
   - Generates structured revision notes with executive summaries, key concepts, and formatted LaTeX formulas.

2. **✍️ Handwritten Notes Scanner & Polish**:
   - Ingests photos or PDFs of handwritten notebook pages using **Sarvam Vision** (`client.doc_ai.digitise`).
   - Uses **Sarvam-105B** to fix OCR shorthand, correct broken formulas, and expand brief notes into textbook-grade explanations.

3. **🔄 Master Study Guide Synthesis**:
   - Merges audio lecture transcripts with student handwritten notebook scans to create a unified study guide.

4. **🧠 Quizzes & Mock Test Arena**:
   - **Interactive MCQ Quizzes**: Configurable question count and difficulty with immediate grading, choice analysis, and detailed explanations.
   - **Full Formal Practice Exams**: Generates Section A (Concept checks), Section B (Analytical problems), Section C (Deep-dive questions), and an Answer Key with a step-by-step marking rubric.
   - **Active-Recall Flashcards**: Expandable flashcards for quick revision.

---

## 🏗️ Architecture & Model Stack

| Component | Sarvam AI Model / API | Role |
|---|---|---|
| **Audio Transcription** | `saaras:v3` (Speech-to-Text) | Speech-to-text with Indic language & Hinglish support |
| **Handwritten OCR** | `Sarvam Vision` (`doc_ai.digitise`) | Digitises handwritten notes and document scans |
| **Note Structuring & LLM** | `sarvam-105b-conversations` | 105B parameter LLM for deep reasoning and note synthesis |
| **Quiz & Test Generation** | `sarvam-105b-conversations` | Structured MCQ generation and exam drafting |

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/Shankhadeep998/sarvam-studygenius.git
cd sarvam-studygenius
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Key
Create a `.env` file in the project root:
```env
SARVAM_API_KEY=your_sarvam_api_key_here
```
*(Never commit your `.env` file; it is listed in `.gitignore`.)*

### 4. Launch the Streamlit App
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Testing

Run the automated integration tests:
```bash
python test_services.py
```

---

## 📄 License
MIT License
