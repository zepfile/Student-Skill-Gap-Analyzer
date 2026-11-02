"""
Student Skill Gap Analyzer - Core Application Server
Powered by Python, Flask, Pandas, SQLite, and Scikit-Learn NLP.
Directly integrated with Student_Skill_Gap_Analyzer_Sample_Database.
"""
import os
import sys
import json
from pathlib import Path

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from flask import Flask, render_template, request, jsonify, Response
from werkzeug.utils import secure_filename

from analyzer.db_manager import DatabaseManager
from analyzer.nlp_engine import NLPEngine
from analyzer.resume_parser import ResumeParser
from analyzer.gap_analyzer import SkillGapAnalyzer
from analyzer.roadmap_generator import RoadmapGenerator
from analyzer.ats_scorer import ATSScorer
from analyzer.skill_quiz import SkillQuizEngine

app = Flask(__name__)
app.config["SECRET_KEY"] = "skillgap-analyzer-super-secret-key-2026"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "uploads")
app.config["TEMPLATES_AUTO_RELOAD"] = True

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# 1. Initialize SQLite Database from Student_Skill_Gap_Analyzer_Sample_Database
db_manager = DatabaseManager()
ROLES_LIST = db_manager.get_all_roles()
ROLES_MAP = {r["role_id"]: r for r in ROLES_LIST}
SKILLS_DICT = db_manager.get_all_skills_dictionary()

# 2. Initialize Core Analytic Engines
nlp_engine = NLPEngine(SKILLS_DICT)
resume_parser = ResumeParser()
gap_analyzer = SkillGapAnalyzer(ROLES_LIST, SKILLS_DICT, nlp_engine)
roadmap_gen = RoadmapGenerator(SKILLS_DICT)
ats_scorer = ATSScorer()
quiz_engine = SkillQuizEngine()


@app.route("/")
def index():
    """Serves the main single-page dashboard with database-driven job roles."""
    roles_display = []
    for r in ROLES_LIST:
        roles_display.append({
            "id": r["role_id"],
            "title": r["title"],
            "category": r["category"],
            "description": r["description"],
            "market_demand": 9.2,
            "growth_rate": "+24% YoY Growth",
            "avg_salary": "₹8 - ₹18 LPA / $85k - $120k",
            "top_industries": ["Tech Startups", "FinTech", "Enterprise Software", "Analytics"]
        })
    return render_template("index.html", roles=roles_display)


@app.route("/api/roles", methods=["GET"])
def get_roles():
    """Returns all available job roles loaded from SQLite / CSV database."""
    return jsonify({"success": True, "roles": ROLES_MAP})


@app.route("/api/skills", methods=["GET"])
def get_skills():
    """Returns the skills catalog with resources and importance weights."""
    return jsonify({"success": True, "skills": SKILLS_DICT})


@app.route("/api/sample-resume/<sample_type>", methods=["GET"])
def get_sample_resume(sample_type):
    """Returns pre-loaded sample resume text for instant demo testing."""
    sample_files = {
        "python_developer": "sample_python_developer_resume.txt",
        "1": "sample_python_developer_resume.txt",
        "data_analyst": "sample_data_analyst_resume.txt",
        "4": "sample_data_analyst_resume.txt",
        "web_developer": "sample_web_developer_resume.txt",
        "3": "sample_web_developer_resume.txt",
        "software_engineer": "sample_python_developer_resume.txt",
        "5": "sample_python_developer_resume.txt",
        "java_developer": "sample_python_developer_resume.txt",
        "2": "sample_python_developer_resume.txt"
    }

    filename = sample_files.get(str(sample_type).lower()) or "sample_python_developer_resume.txt"
    sample_path = Path(__file__).parent / "sample_data" / filename

    if not sample_path.exists():
        return jsonify({"success": False, "error": f"Sample resume file not found."}), 404

    with open(sample_path, "r", encoding="utf-8") as f:
        content = f.read()

    return jsonify({"success": True, "sample_text": content, "filename": filename})


@app.route("/api/analyze", methods=["POST"])
def analyze_resume():
    """
    Core pipeline:
    1. Parse resume text from PDF, DOCX, or direct text payload
    2. Extract candidate skills using NLP engine
    3. Analyze gap against chosen target role from SQLite database
    4. Compute ATS resume compatibility score
    5. Generate structured learning roadmap with database resources
    6. Persist assessment record to SQLite database
    """
    try:
        resume_text = ""
        filename = "pasted_resume.txt"

        # Check if file uploaded
        if "resume_file" in request.files and request.files["resume_file"].filename != "":
            file = request.files["resume_file"]
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)

            resume_text = resume_parser.extract_text_from_file(file_path)

            try:
                os.remove(file_path)
            except OSError:
                pass
        else:
            # Check for direct text payload
            resume_text = request.form.get("resume_text", "")
            if not resume_text and request.is_json:
                data = request.get_json() or {}
                resume_text = data.get("resume_text", "")

        if not resume_text or not resume_text.strip():
            return jsonify({"success": False, "error": "No resume content detected. Please upload a PDF/DOCX or paste your resume text."}), 400

        target_role_id = request.form.get("role_id")
        if not target_role_id and request.is_json:
            target_role_id = (request.get_json() or {}).get("role_id")

        if not target_role_id:
            target_role_id = ROLES_LIST[0]["role_id"] if ROLES_LIST else "1"

        target_role_id = str(target_role_id)

        # 1. NLP Text Analysis & Skill Extraction
        detected_skills = nlp_engine.extract_skills(resume_text)
        detected_skill_names = [s["name"] for s in detected_skills]
        contact_info = nlp_engine.extract_contact_info(resume_text)
        sections = resume_parser.extract_sections(resume_text)

        # 2. Pandas Skill Gap Analysis against SQLite Database
        fit_analysis = gap_analyzer.analyze_role_fit(detected_skill_names, target_role_id, resume_text)

        # 3. Learning Roadmap Generation with database resources
        roadmap = roadmap_gen.generate_roadmap(fit_analysis)

        # 4. ATS Resume Compatibility Scoring
        ats_feedback = ats_scorer.evaluate(resume_text, detected_skills_count=len(detected_skill_names))

        # 5. Multi-Role Compatibility Rankings
        role_comparisons = gap_analyzer.compare_all_roles(detected_skill_names, resume_text)

        # 6. Save Assessment Record to SQLite
        email_val = contact_info.get("email") or "candidate@student.edu"
        student_name = email_val.split("@")[0].replace(".", " ").title()
        db_manager.save_assessment(
            candidate_name=student_name,
            target_role=fit_analysis["role_title"],
            readiness_score=fit_analysis["readiness_score"],
            ats_score=ats_feedback["overall_score"],
            matched_count=fit_analysis["total_matched_skills"],
            missing_count=len(fit_analysis["missing_core"]) + len(fit_analysis["missing_secondary"])
        )

        return jsonify({
            "success": True,
            "candidate_profile": {
                "filename": filename,
                "contact_info": contact_info,
                "detected_sections": list(sections.keys()),
                "extracted_skills": detected_skills,
                "total_skills_found": len(detected_skills),
                "raw_text_snippet": resume_text[:600] + ("..." if len(resume_text) > 600 else "")
            },
            "fit_analysis": fit_analysis,
            "roadmap": roadmap,
            "ats_feedback": ats_feedback,
            "role_comparisons": role_comparisons
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/analyze-custom-jd", methods=["POST"])
def analyze_custom_jd():
    """Analyzes a student's extracted skills against an ad-hoc pasted Job Description."""
    try:
        data = request.get_json() or {}
        jd_text = data.get("jd_text", "").strip()
        student_skills = data.get("student_skills", [])

        if not jd_text:
            return jsonify({"success": False, "error": "Job description text cannot be empty."}), 400

        result = gap_analyzer.analyze_custom_jd(student_skills, jd_text)
        return jsonify({"success": True, "analysis": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/skill-quiz/<skill_name>", methods=["GET"])
def get_skill_quiz(skill_name):
    """Returns a 3-question diagnostic quiz for self-assessment."""
    try:
        quiz_data = quiz_engine.get_quiz_for_skill(skill_name)
        return jsonify({"success": True, "skill": skill_name, "quiz": quiz_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/assessment-history", methods=["GET"])
def get_assessment_history():
    """Returns recent student assessment history from SQLite database."""
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, candidate_name, target_role, readiness_score, ats_score, 
                   matched_skills_count, missing_skills_count, assessed_at 
            FROM assessment_history 
            ORDER BY id DESC LIMIT 15
        """)
        history = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify({"success": True, "history": history})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/ats/polish-bullet", methods=["POST"])
def polish_bullet():
    """Generates high-impact STAR power verb variations for any bullet point."""
    try:
        data = request.get_json() or {}
        bullet = data.get("bullet", "").strip()
        skill = data.get("skill", "")
        if not bullet:
            return jsonify({"success": False, "error": "Bullet text cannot be empty."}), 400

        result = ats_scorer.polish_bullet(bullet, target_skill=skill)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/export-report", methods=["POST"])
def export_report():
    """Exports structured Markdown assessment report for download or PDF generation."""
    try:
        data = request.get_json() or {}
        fit = data.get("fit_analysis", {})
        candidate = data.get("candidate_profile", {})
        roadmap = data.get("roadmap", {})
        ats = data.get("ats_feedback", {})

        report_lines = [
            f"# 🎯 Skill Gap Assessment Report: {fit.get('role_title', 'Role')}",
            f"> **Generated For:** {candidate.get('filename', 'Candidate Resume')}",
            f"> **Job Readiness Score:** {fit.get('readiness_score', 0)}% ({fit.get('readiness_level', 'N/A')})",
            f"> **ATS Resume Score:** {ats.get('overall_score', 0)} / 100 ({ats.get('tier', 'Good')})\n",
            "---",
            f"## 📊 Verified Competencies vs Gaps",
            f"- **Verified Core Competencies:** {', '.join(fit.get('matched_core', [])) or 'None'}",
            f"- **Critical Must-Have Gaps:** {', '.join(fit.get('missing_core', [])) or 'None'}",
            f"- **Secondary Gaps:** {', '.join(fit.get('missing_secondary', [])) or 'None'}\n",
            f"## 🗺️ Curated Learning Roadmap",
            f"- **Estimated Timeline:** {roadmap.get('estimated_weeks', 0)} Weeks (~{roadmap.get('estimated_hours', 0)} Total Hours)\n"
        ]

        for p in roadmap.get("phases", []):
            report_lines.append(f"### {p.get('title')} ({p.get('duration')})")
            report_lines.append(f"*{p.get('focus')}*")
            if p.get("project_name"):
                report_lines.append(f"- **Capstone Project**: {p.get('project_name')}")
            for s in p.get("skills", []):
                report_lines.append(f"- **{s.get('skill')}**: {s.get('action_item')}")
            report_lines.append("")

        report_lines.append("## 📝 ATS Resume Polish Recommendations")
        for sugg in ats.get("suggestions", []):
            report_lines.append(f"- {sugg}")

        report_md = "\n".join(report_lines)

        return Response(
            report_md,
            mimetype="text/markdown",
            headers={"Content-Disposition": f"attachment;filename=SkillGap_Assessment_{fit.get('role_id', 'report')}.md"}
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    print("=" * 60)
    print("[*] Student Skill Gap Analyzer is starting...")
    print("[*] SQLite Database connected: skill_gap.db")
    print("[*] Access the web application at: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=False)
