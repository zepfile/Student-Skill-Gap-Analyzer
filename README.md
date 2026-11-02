# 🎯 Student Skill Gap Analyzer

An intelligent, full-stack AI/NLP web application built with **Python**, **Flask**, **SQLite**, **Pandas**, and **Scikit-Learn NLP**. Directly integrated with the official `Student_Skill_Gap_Analyzer_Sample_Database` to benchmark student resumes against industry standards, quantify skill gaps, calculate ATS resume hygiene scores, and generate step-by-step learning roadmaps.

---

## 🌟 Core Features & Capabilities

1. **☀️ Day & Night Mode (Theme Toggle)**:
   - High-contrast, responsive theme switcher between **Day (Light)** and **Night (Dark)** modes.
   - Text colors, badges, cards, navigation bar, and modals dynamically adapt with zero illegibility.
   - Saves theme preference in browser `localStorage`.
   - Chart.js radar and doughnut visualizations dynamically refresh with matching gridlines and label contrasts.

2. **🗄️ SQLite Database Integration (`Student_Skill_Gap_Analyzer_Sample_Database`)**:
   - Seeded automatically from:
     - `job_roles.csv`: Industry job profiles (`Python Developer`, `Java Developer`, `Web Developer`, `Data Analyst`, `Software Engineer`).
     - `job_skills.csv`: Skill mappings with proficiency levels (1-3) and importance weights (1-5).
     - `learning_resources.csv`: Official courses, documentation, and tutorials for every required competency.
   - Persists all student assessments in the `assessment_history` SQLite table.

3. **🔍 NLP-Powered Skill Extraction & Semantic Matching**:
   - Boundary-aware regex and canonical alias mapping for tech skills (e.g. `dsa` ↔ `Data Structures and Algorithms`, `html5` ↔ `HTML`, `js` ↔ `JavaScript`, `postgres` ↔ `SQL`).
   - **TF-IDF Vectorization & Cosine Similarity** to compare candidate resume text against target role profiles.
   - Extracts contact details (Email, Phone, GitHub, LinkedIn) and structural sections (Summary, Skills, Experience, Education, Projects).

4. **📊 Pandas-Driven Gap Analysis Engine**:
   - Categorizes skills into **Core Must-Have (Importance Weight >= 4, 2x factor)** and **Secondary Competencies (Importance Weight < 4, 1x factor)**.
   - Computes an aggregate **Job Readiness Index (%)**.
   - Generates interactive **Domain Competency Radar Chart** and **Role Coverage Doughnut Chart**.

5. **⚡ Interactive Live Skill Check-off & Score Recalculator**:
   - Students can check off skills as *"Mark as Learned / I already know this"* in the gap checklist.
   - Instantly recalculates the **Job Readiness Score**, updates the progress bar, and updates the **Doughnut Chart live** without reloading the page.

6. **📋 Applicant Tracking System (ATS) Resume Health Scorer**:
   - Computes an **ATS Compatibility Score (0 - 100)**.
   - Measures **Action Verb Density** (*Spearheaded, Architected, Engineered, Optimized, Automated*).
   - Detects **Quantifiable Metrics & Percentages** (*e.g., latency reduced by 35%, 50,000 requests*).
   - Verifies **Section Completeness** and provides actionable suggestions to boost resume ranking.
   - **⚡ ATS Power Verb Re-writer (Instant Word Swapper)**:
     - Scans student resumes for passive or weak phrases (*e.g., "worked on", "responsible for", "handled", "assisted with"*).
     - Renders side-by-side **Before ➔ After** transformation cards with 1-click clipboard copy.
     - Includes an interactive **Bullet Polisher Sandbox** generating 3 high-impact STAR variations (Performance, Architecture, Automation) with quantifiable metrics.
     - Features a comprehensive **Recruiter Power Action Verbs Taxonomy** organized by technical intent.

7. **🧠 Interactive Skill Diagnostic Quiz Engine**:
   - One-click *"Test Yourself"* diagnostic quizzes for skills with instant scoring and explanations.

8. **🗺️ Actionable Learning Roadmap & Interview Prep**:
   - Phased study plan with time estimates (weeks & hours).
   - Curated courses from the database.
   - Capstone portfolio project ideas with concrete deliverables.
   - Frequently asked technical interview questions with answer guidelines.

9. **🌐 Multi-Role Compatibility Matrix**:
   - Cross-analyzes the student's profile across all 5 database roles simultaneously with 1-click "View Gaps" role switching.

10. **📝 Custom Job Description Gap Analyzer**:
    - Paste any job posting from LinkedIn or Indeed to calculate direct skill match and TF-IDF semantic alignment against that specific posting.

11. **📄 Export Assessment Report (.md)**:
    - 1-click export of a structured Markdown assessment report for offline review or portfolio documentation.

---

## 📁 Clean Folder Structure

```
Student Skill Gap Analyzer/
├── app.py                     # Flask web server & REST API endpoints
├── skill_gap.db               # SQLite database (auto-seeded from CSVs)
├── requirements.txt           # Python package dependencies
├── test_app.py                # Comprehensive unit & integration test suite
├── run.bat                    # One-click Windows launch script
├── README.md                  # Project documentation
│
├── analyzer/                  # Core analytic modules
│   ├── __init__.py
│   ├── db_manager.py          # SQLite manager & CSV seeder
│   ├── nlp_engine.py          # NLP tokenization & skill extraction
│   ├── gap_analyzer.py        # Pandas role comparison & readiness scoring
│   ├── resume_parser.py       # PDF/DOCX/TXT text extraction
│   ├── ats_scorer.py          # ATS resume hygiene & verb density scoring
│   ├── roadmap_generator.py   # Phased study curriculum & interview questions
│   └── skill_quiz.py          # 3-question skill diagnostic quizzes
│
├── sample_data/               # Pre-loaded sample resumes for instant demo testing
│   ├── sample_python_developer_resume.txt
│   ├── sample_data_analyst_resume.txt
│   └── sample_web_developer_resume.txt
│
├── static/
│   ├── css/
│   │   └── style.css          # Modern UI stylesheet with full Day/Night mode support
│   └── js/
│       └── app.js             # Client-side controller, Chart.js, & event listeners
│
├── templates/
│   └── index.html             # Single-page dashboard template
│
└── Student_Skill_Gap_Analyzer_Sample_Database/  # Original sample CSV database
    ├── job_roles.csv
    ├── job_skills.csv
    ├── learning_resources.csv
    └── README.txt
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
Ensure you have Python 3.9+ installed.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Unit Tests
```bash
python -m unittest test_app.py
```
*(All 11 integration and unit tests will pass).*

### 4. Start the Application
```bash
python app.py
```
Or double-click `run.bat` on Windows.

### 5. Access the Web Application
Open your browser and navigate to:
```
http://127.0.0.1:5000
```
