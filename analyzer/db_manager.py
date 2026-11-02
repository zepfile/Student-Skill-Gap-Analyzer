"""
SQLite Database Manager for Student Skill Gap Analyzer
Imports and manages data from Student_Skill_Gap_Analyzer_Sample_Database:
- job_roles.csv
- job_skills.csv
- learning_resources.csv
Provides query interfaces for roles, skills, weights, and learning resources.
"""
import os
import csv
import sqlite3
from pathlib import Path


class DatabaseManager:
    def __init__(self, db_path: str = None, csv_dir: str = None):
        base_dir = Path(__file__).resolve().parent.parent
        self.csv_dir = Path(csv_dir) if csv_dir else base_dir / "Student_Skill_Gap_Analyzer_Sample_Database"
        self.db_path = Path(db_path) if db_path else base_dir / "skill_gap.db"
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Creates SQLite tables and seeds them from CSV files."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create Tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_roles (
                role_id INTEGER PRIMARY KEY,
                job_role TEXT NOT NULL,
                description TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role_id INTEGER NOT NULL,
                job_role TEXT NOT NULL,
                skill TEXT NOT NULL,
                required_level INTEGER NOT NULL,
                importance_weight INTEGER NOT NULL,
                FOREIGN KEY (role_id) REFERENCES job_roles(role_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                resource_name TEXT NOT NULL,
                resource_url TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assessment_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_name TEXT,
                target_role TEXT NOT NULL,
                readiness_score REAL NOT NULL,
                ats_score REAL NOT NULL,
                matched_skills_count INTEGER,
                missing_skills_count INTEGER,
                assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()

        # Seed data from CSV if tables are empty
        cursor.execute("SELECT COUNT(*) FROM job_roles")
        if cursor.fetchone()[0] == 0:
            self._seed_from_csv(conn)

        conn.close()

    def _seed_from_csv(self, conn):
        """Reads CSV files from Student_Skill_Gap_Analyzer_Sample_Database and populates SQLite."""
        cursor = conn.cursor()

        # 1. Seed job_roles.csv
        roles_file = self.csv_dir / "job_roles.csv"
        if roles_file.exists():
            with open(roles_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cursor.execute("""
                        INSERT OR REPLACE INTO job_roles (role_id, job_role, description)
                        VALUES (?, ?, ?)
                    """, (int(row["role_id"]), row["job_role"].strip(), row["description"].strip()))

        # 2. Seed job_skills.csv
        skills_file = self.csv_dir / "job_skills.csv"
        if skills_file.exists():
            with open(skills_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cursor.execute("""
                        INSERT INTO job_skills (role_id, job_role, skill, required_level, importance_weight)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        int(row["role_id"]),
                        row["job_role"].strip(),
                        row["skill"].strip(),
                        int(row["required_level"]),
                        int(row["importance_weight"])
                    ))

        # 3. Seed learning_resources.csv
        resources_file = self.csv_dir / "learning_resources.csv"
        if resources_file.exists():
            with open(resources_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cursor.execute("""
                        INSERT INTO learning_resources (skill, resource_type, resource_name, resource_url)
                        VALUES (?, ?, ?, ?)
                    """, (
                        row["skill"].strip(),
                        row["resource_type"].strip(),
                        row["resource_name"].strip(),
                        row["resource_url"].strip()
                    ))

        conn.commit()

    def get_all_roles(self) -> list:
        """Returns all job roles with their required skills and metadata."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT role_id, job_role, description FROM job_roles ORDER BY role_id")
        roles = []
        for row in cursor.fetchall():
            role_id = row["role_id"]
            # Fetch skills for this role
            cursor.execute("""
                SELECT skill, required_level, importance_weight 
                FROM job_skills 
                WHERE role_id = ? 
                ORDER BY importance_weight DESC
            """, (role_id,))
            skills = [dict(s) for s in cursor.fetchall()]

            # Categorize into core (importance_weight >= 4) and secondary (importance_weight < 4)
            core_skills = [s["skill"] for s in skills if s["importance_weight"] >= 4]
            secondary_skills = [s["skill"] for s in skills if s["importance_weight"] < 4]

            roles.append({
                "role_id": str(role_id),
                "title": row["job_role"],
                "description": row["description"],
                "category": self._infer_role_category(row["job_role"]),
                "skills": skills,
                "core_skills": core_skills,
                "secondary_skills": secondary_skills
            })

        conn.close()
        return roles

    def get_role_by_id(self, role_id) -> dict:
        """Fetches a specific role by its ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT role_id, job_role, description FROM job_roles WHERE role_id = ?", (int(role_id),))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None

        cursor.execute("""
            SELECT skill, required_level, importance_weight 
            FROM job_skills 
            WHERE role_id = ? 
            ORDER BY importance_weight DESC
        """, (int(role_id),))
        skills = [dict(s) for s in cursor.fetchall()]
        conn.close()

        core_skills = [s["skill"] for s in skills if s["importance_weight"] >= 4]
        secondary_skills = [s["skill"] for s in skills if s["importance_weight"] < 4]

        return {
            "role_id": str(row["role_id"]),
            "title": row["job_role"],
            "description": row["description"],
            "category": self._infer_role_category(row["job_role"]),
            "skills": skills,
            "core_skills": core_skills,
            "secondary_skills": secondary_skills
        }

    def get_resources_for_skill(self, skill: str) -> list:
        """Fetches learning resources for a given skill from SQLite."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT resource_type, resource_name, resource_url 
            FROM learning_resources 
            WHERE LOWER(skill) = LOWER(?)
        """, (skill,))
        resources = []
        for r in cursor.fetchall():
            resources.append({
                "type": r["resource_type"],
                "title": r["resource_name"],
                "url": r["resource_url"]
            })
        conn.close()
        return resources

    def get_all_skills_dictionary(self) -> dict:
        """Constructs canonical skill dictionary from SQLite with resources and weights."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT skill, MAX(importance_weight) as max_weight 
            FROM job_skills 
            GROUP BY skill
        """)
        skills_dict = {}
        for row in cursor.fetchall():
            skill_name = row["skill"]
            weight = row["max_weight"]
            resources = self.get_resources_for_skill(skill_name)
            skills_dict[skill_name] = {
                "name": skill_name,
                "importance_weight": weight,
                "category": self._infer_skill_category(skill_name),
                "resources": resources
            }
        conn.close()
        return skills_dict

    def save_assessment(self, candidate_name: str, target_role: str, readiness_score: float, ats_score: float, matched_count: int, missing_count: int):
        """Saves an assessment record to SQLite."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO assessment_history 
            (candidate_name, target_role, readiness_score, ats_score, matched_skills_count, missing_skills_count)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (candidate_name, target_role, readiness_score, ats_score, matched_count, missing_count))
        conn.commit()
        conn.close()

    def _infer_role_category(self, role_title: str) -> str:
        t = role_title.lower()
        if "data" in t or "analyst" in t:
            return "Data & Analytics"
        if "web" in t or "frontend" in t:
            return "Web Development"
        if "python" in t or "backend" in t:
            return "Backend & Scripting"
        if "java" in t:
            return "Enterprise Java"
        return "Software Engineering"

    def _infer_skill_category(self, skill: str) -> str:
        s = skill.lower()
        if s in ["python", "java", "javascript", "c", "c++", "sql"]:
            return "Programming Languages"
        if s in ["html", "css", "flask", "pandas", "rest apis"]:
            return "Frameworks & Libraries"
        if s in ["git", "excel"]:
            return "Tools & Version Control"
        if s in ["data visualization"]:
            return "Analytics & Reporting"
        if s in ["data structures and algorithms", "oop", "testing and debugging"]:
            return "Computer Science Core"
        return "Technical Skills"

