"""
Automated Integration and Unit Test Suite for Student Skill Gap Analyzer
Directly tests SQLite database integration, NLP engine, ATS scoring, gap analysis,
quiz generation, and report export.
"""
import io
import unittest
import json
from app import app, db_manager, nlp_engine, gap_analyzer, roadmap_gen, ats_scorer, quiz_engine


class TestSkillGapAnalyzer(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_routes_health(self):
        """Test home page and catalog APIs."""
        res = self.app.get("/")
        self.assertEqual(res.status_code, 200)

        res_roles = self.app.get("/api/roles")
        self.assertEqual(res_roles.status_code, 200)
        data = res_roles.get_json()
        self.assertTrue(data["success"])
        # Should contain roles from sample database (e.g. 1, 2, 3, 4, 5)
        self.assertGreaterEqual(len(data["roles"]), 5)

        res_skills = self.app.get("/api/skills")
        self.assertEqual(res_skills.status_code, 200)
        skills_data = res_skills.get_json()
        self.assertTrue(skills_data["success"])
        self.assertIn("Python", skills_data["skills"])

    def test_database_manager(self):
        """Verify SQLite tables seeded from Student_Skill_Gap_Analyzer_Sample_Database."""
        conn = db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM job_roles")
        role_count = cursor.fetchone()[0]
        self.assertGreaterEqual(role_count, 5)

        cursor.execute("SELECT COUNT(*) FROM job_skills")
        skills_count = cursor.fetchone()[0]
        self.assertGreaterEqual(skills_count, 15)

        cursor.execute("SELECT COUNT(*) FROM learning_resources")
        res_count = cursor.fetchone()[0]
        self.assertGreaterEqual(res_count, 10)

        conn.close()

    def test_sample_resume_endpoint(self):
        """Test pre-loaded sample resumes."""
        res = self.app.get("/api/sample-resume/python_developer")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("Python", data["sample_text"])

        res_da = self.app.get("/api/sample-resume/data_analyst")
        self.assertEqual(res_da.status_code, 200)
        self.assertTrue(res_da.get_json()["success"])

    def test_nlp_extraction(self):
        """Test skill extraction and contact details."""
        text = "Contact: rohan.sharma@email.com, +91 9876543210. Experienced in Python, Flask, Pandas, SQL, and Git."
        info = nlp_engine.extract_contact_info(text)
        self.assertEqual(info["email"], "rohan.sharma@email.com")
        self.assertIsNotNone(info["phone"])

        skills = nlp_engine.extract_skills(text)
        skill_names = [s["name"] for s in skills]
        self.assertIn("Python", skill_names)
        self.assertIn("Flask", skill_names)
        self.assertIn("SQL", skill_names)
        self.assertIn("Git", skill_names)

    def test_ats_scorer(self):
        """Test ATS Resume Hygiene Scorer."""
        sample_resume = """
        Rohan Sharma
        rohan@example.com | 9876543210
        Summary:
        Motivated software engineer with experience in building web APIs and clean backends.
        Technical Skills:
        Python, Flask, SQL, HTML, CSS, JavaScript, Git
        Experience:
        - Spearheaded and engineered a backend REST API that reduced latency by 35%.
        - Developed data extraction pipelines processing 50,000 requests per day.
        Projects:
        - Built an automated portfolio management system in Python.
        Education:
        B.Tech in Computer Science, GPA: 8.8
        """
        ats_result = ats_scorer.evaluate(sample_resume, detected_skills_count=7)
        self.assertGreaterEqual(ats_result["overall_score"], 60.0)
        self.assertIn("Spearheaded", ats_result["action_verbs_found"])
        self.assertGreater(ats_result["metrics_detected"], 0)
        self.assertIn("power_verb_categories", ats_result)

    def test_ats_polish_bullet_endpoint(self):
        """Test ATS Power Verb Re-writer endpoint."""
        # Unit test method
        polished = ats_scorer.polish_bullet("Worked on Python scripts for data cleaning", target_skill="Python")
        self.assertEqual(polished["detected_weak_verb"], "worked on")
        self.assertEqual(len(polished["variations"]), 3)
        self.assertIn("Optimized", [v["power_verb"] for v in polished["variations"]])

        # API endpoint test
        payload = {
            "bullet": "Responsible for web development using HTML and CSS",
            "skill": "HTML/CSS"
        }
        res = self.app.post("/api/ats/polish-bullet", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertGreaterEqual(len(data["result"]["variations"]), 3)

    def test_skill_quiz_endpoint(self):
        """Test Diagnostic Quiz API for skills."""
        res = self.app.get("/api/skill-quiz/Python")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertGreaterEqual(len(data["quiz"]["questions"]), 3)
        self.assertEqual(data["quiz"]["questions"][0]["correct_index"], 0)

    def test_analyze_pipeline(self):
        """Test full analysis endpoint with sample text payload against Python Developer role."""
        sample_resume = """
        Rohan Sharma
        rohan@example.com | 9876543210
        Skills: Python, Flask, Pandas, SQL, Git
        Experience:
        Spearheaded the development of backend services and optimized SQL queries by 40%.
        Projects:
        REST API service with Flask and PostgreSQL.
        Education:
        Bachelor of Technology in Computer Science.
        """
        payload = {
            "role_id": "1",  # Python Developer in sample database
            "resume_text": sample_resume
        }
        res = self.app.post("/api/analyze", data=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertGreater(data["fit_analysis"]["readiness_score"], 40.0)
        self.assertIn("ats_feedback", data)
        self.assertIn("radar_chart_data", data["fit_analysis"])
        self.assertIn("phases", data["roadmap"])
        self.assertGreaterEqual(len(data["role_comparisons"]), 5)

    def test_analyze_file_upload(self):
        """Test uploading a file to /api/analyze."""
        file_content = b"""
        Priya Patel
        Email: priya@example.com
        Technical Skills: HTML, CSS, JavaScript, REST APIs, Git
        """
        data = {
            "role_id": "3",  # Web Developer
            "resume_file": (io.BytesIO(file_content), "resume.txt")
        }
        res = self.app.post("/api/analyze", data=data, content_type="multipart/form-data")
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertTrue(json_data["success"])
        extracted_names = [s["name"] for s in json_data["candidate_profile"]["extracted_skills"]]
        self.assertIn("JavaScript", extracted_names)

    def test_custom_jd_analysis(self):
        """Test custom Job Description evaluation."""
        payload = {
            "student_skills": ["Python", "SQL", "Flask"],
            "jd_text": "Looking for a backend engineer with Python, Flask, REST APIs, and SQL."
        }
        res = self.app.post("/api/analyze-custom-jd", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("Python", data["analysis"]["matched_skills"])

    def test_export_report_endpoint(self):
        """Test generating downloadable markdown assessment report."""
        dummy_payload = {
            "fit_analysis": {
                "role_id": "1",
                "role_title": "Python Developer",
                "readiness_score": 85.0,
                "readiness_level": "Job Ready",
                "matched_core": ["Python", "SQL"],
                "missing_core": ["REST APIs"]
            },
            "roadmap": {
                "estimated_weeks": 4,
                "estimated_hours": 48,
                "phases": []
            },
            "ats_feedback": {
                "overall_score": 88,
                "tier": "Good",
                "suggestions": ["Add more metrics"]
            }
        }
        res = self.app.post("/api/export-report", json=dummy_payload)
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/markdown", res.headers.get("Content-Type", ""))
        self.assertIn("Skill Gap Assessment Report", res.get_data(as_text=True))

    def test_assessment_history_endpoint(self):
        """Test assessment history endpoint."""
        res = self.app.get("/api/assessment-history")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIsInstance(data["history"], list)


if __name__ == "__main__":
    unittest.main()
