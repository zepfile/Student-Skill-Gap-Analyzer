import pandas as pd
import numpy as np


class SkillGapAnalyzer:
    def __init__(self, roles_db: dict, skills_db: dict, nlp_engine):
        """
        Initializes the analyzer with roles taxonomy and skills database.
        """
        if isinstance(roles_db, list):
            self.roles = {str(r["role_id"]): r for r in roles_db}
            for r in roles_db:
                self.roles[r["title"].lower().replace(" ", "_")] = r
        elif isinstance(roles_db, dict) and "roles" in roles_db:
            self.roles = roles_db["roles"]
        else:
            self.roles = roles_db if isinstance(roles_db, dict) else {}

        self.skills_db = skills_db.get("skills", {}) if isinstance(skills_db, dict) and "skills" in skills_db else (skills_db or {})
        self.nlp = nlp_engine

    def analyze_role_fit(self, student_skills: list, target_role_id: str, resume_text: str = "") -> dict:
        """
        Performs in-depth skill gap analysis for a chosen target role.
        """
        str_id = str(target_role_id)
        if str_id in self.roles:
            role_info = self.roles[str_id]
        else:
            matched_key = next((k for k, v in self.roles.items() if v.get("title", "").lower() == str_id.lower() or k.lower() == str_id.lower()), None)
            if matched_key:
                role_info = self.roles[matched_key]
            elif self.roles:
                role_info = list(self.roles.values())[0]
            else:
                raise ValueError(f"No roles loaded in taxonomy.")

        role_info = self.roles[target_role_id]
        role_title = role_info.get("title", target_role_id)
        core_required = set(role_info.get("core_skills", []))
        secondary_required = set(role_info.get("secondary_skills", []))
        soft_required = set(role_info.get("soft_skills", []))

        # Extracted student skill names
        student_skill_names = {s["name"] if isinstance(s, dict) else s for s in student_skills}

        # Calculate Matches and Gaps
        matched_core = sorted(list(core_required.intersection(student_skill_names)))
        missing_core = sorted(list(core_required.difference(student_skill_names)))

        matched_secondary = sorted(list(secondary_required.intersection(student_skill_names)))
        missing_secondary = sorted(list(secondary_required.difference(student_skill_names)))

        matched_soft = sorted(list(soft_required.intersection(student_skill_names)))
        missing_soft = sorted(list(soft_required.difference(student_skill_names)))

        all_role_skills = core_required.union(secondary_required).union(soft_required)
        bonus_skills = sorted(list(student_skill_names.difference(all_role_skills)))

        # Weighted Readiness Computation using Pandas
        core_weight = 2.0
        sec_weight = 1.0
        soft_weight = 0.5

        total_possible_points = (
            len(core_required) * core_weight +
            len(secondary_required) * sec_weight +
            len(soft_required) * soft_weight
        )

        earned_points = (
            len(matched_core) * core_weight +
            len(matched_secondary) * sec_weight +
            len(matched_soft) * soft_weight
        )

        skill_coverage_pct = round((earned_points / total_possible_points * 100), 1) if total_possible_points > 0 else 0.0

        # NLP Semantic Similarity between Resume Text and Role Specification
        role_corpus = f"{role_title} {role_info.get('description', '')} {' '.join(core_required)} {' '.join(secondary_required)}"
        nlp_similarity = self.nlp.compute_similarity(resume_text, role_corpus) if resume_text else (skill_coverage_pct / 100.0)

        # Composite Readiness Index (75% Skill Coverage + 25% Semantic Text Similarity)
        readiness_score = round((skill_coverage_pct * 0.75) + (nlp_similarity * 100.0 * 0.25), 1)
        readiness_score = min(100.0, max(0.0, readiness_score))

        # Readiness Level classification
        if readiness_score >= 80:
            readiness_level = "Job Ready (High Match)"
            readiness_badge = "success"
        elif readiness_score >= 60:
            readiness_level = "Intermediate (Moderate Gaps)"
            readiness_badge = "primary"
        elif readiness_score >= 40:
            readiness_level = "Developing (Noticeable Gaps)"
            readiness_badge = "warning"
        else:
            readiness_level = "Novice / Foundational (Significant Gaps)"
            readiness_badge = "danger"

        # Categorized Gap Priority Details with resources
        gap_items = []
        for s in missing_core:
            meta = self.skills_db.get(s, {})
            gap_items.append({
                "skill": s,
                "category": meta.get("category", "Core Technical"),
                "priority": "High (Critical)",
                "priority_code": "high",
                "importance": 2.0,
                "resources": meta.get("resources", []),
                "project_ideas": meta.get("project_ideas", [])
            })

        for s in missing_secondary:
            meta = self.skills_db.get(s, {})
            gap_items.append({
                "skill": s,
                "category": meta.get("category", "Secondary Technical"),
                "priority": "Medium",
                "priority_code": "medium",
                "importance": 1.0,
                "resources": meta.get("resources", []),
                "project_ideas": meta.get("project_ideas", [])
            })

        for s in missing_soft:
            meta = self.skills_db.get(s, {})
            gap_items.append({
                "skill": s,
                "category": "Soft Skills & Leadership",
                "priority": "Low",
                "priority_code": "low",
                "importance": 0.5,
                "resources": meta.get("resources", []),
                "project_ideas": meta.get("project_ideas", [])
            })

        # Category Breakdown using Pandas DataFrame
        radar_categories = self._compute_category_radar(student_skill_names, role_info)

        return {
            "role_id": target_role_id,
            "role_title": role_title,
            "role_description": role_info.get("description", ""),
            "market_demand": role_info.get("market_demand", 8.5),
            "growth_rate": role_info.get("growth_rate", "+20% YoY"),
            "avg_salary": role_info.get("avg_salary", "N/A"),
            "salary_percentiles": role_info.get("salary_percentiles", {
                "p25": "$70,000 / ₹7 LPA",
                "median": "$100,000 / ₹15 LPA",
                "p90": "$150,000 / ₹28 LPA"
            }),
            "top_industries": role_info.get("top_industries", ["Tech", "FinTech", "SaaS"]),
            "readiness_score": readiness_score,
            "readiness_level": readiness_level,
            "readiness_badge": readiness_badge,
            "nlp_similarity": round(nlp_similarity * 100, 1),
            "matched_core": matched_core,
            "missing_core": missing_core,
            "matched_secondary": matched_secondary,
            "missing_secondary": missing_secondary,
            "matched_soft": matched_soft,
            "missing_soft": missing_soft,
            "bonus_skills": bonus_skills,
            "total_required_skills": len(all_role_skills),
            "total_matched_skills": len(matched_core) + len(matched_secondary) + len(matched_soft),
            "gap_items": gap_items,
            "radar_chart_data": radar_categories
        }

    def _compute_category_radar(self, student_skills: set, role_info: dict) -> dict:
        """
        Uses Pandas to group skills by category and compute percentage coverage
        for radar / spider chart visualization.
        """
        rows = []
        for s_name in role_info.get("core_skills", []):
            cat = self.skills_db.get(s_name, {}).get("category", "General")
            rows.append({"skill": s_name, "category": cat, "required": 1, "matched": 1 if s_name in student_skills else 0})

        for s_name in role_info.get("secondary_skills", []):
            cat = self.skills_db.get(s_name, {}).get("category", "General")
            rows.append({"skill": s_name, "category": cat, "required": 1, "matched": 1 if s_name in student_skills else 0})

        if not rows:
            return {"labels": ["General"], "student_scores": [0], "benchmark_scores": [100]}

        df = pd.DataFrame(rows)
        grouped = df.groupby("category").agg({"required": "sum", "matched": "sum"}).reset_index()
        grouped["pct_score"] = (grouped["matched"] / grouped["required"] * 100).round(1)

        labels = grouped["category"].tolist()
        student_scores = grouped["pct_score"].tolist()
        benchmark_scores = [100.0] * len(labels)

        return {
            "labels": labels,
            "student_scores": student_scores,
            "benchmark_scores": benchmark_scores
        }

    def compare_all_roles(self, student_skills: list, resume_text: str = "") -> list:
        """
        Runs fit analysis across all defined roles and returns ranked comparison table.
        """
        comparisons = []
        seen_roles = set()
        for role_id, r_info in self.roles.items():
            title = r_info.get("title", str(role_id))
            if title in seen_roles:
                continue
            seen_roles.add(title)
            fit = self.analyze_role_fit(student_skills, role_id, resume_text)
            comparisons.append({
                "role_id": r_info.get("role_id", str(role_id)),
                "role_title": fit["role_title"],
                "readiness_score": fit["readiness_score"],
                "readiness_level": fit["readiness_level"],
                "market_demand": fit.get("market_demand", 9.0),
                "matched_count": fit["total_matched_skills"],
                "total_required": fit["total_required_skills"],
                "missing_core_count": len(fit["missing_core"])
            })

        # Sort descending by readiness score
        df_comp = pd.DataFrame(comparisons)
        df_comp = df_comp.sort_values(by="readiness_score", ascending=False)
        return df_comp.to_dict(orient="records")

    def analyze_custom_jd(self, student_skills: list, jd_text: str) -> dict:
        """
        Extracts skills and requirements from a custom Job Description text and analyzes the gap.
        """
        jd_skills = self.nlp.extract_skills(jd_text)
        jd_skill_names = {s["name"] for s in jd_skills}
        student_skill_names = {s["name"] if isinstance(s, dict) else s for s in student_skills}

        matched = sorted(list(jd_skill_names.intersection(student_skill_names)))
        missing = sorted(list(jd_skill_names.difference(student_skill_names)))
        bonus = sorted(list(student_skill_names.difference(jd_skill_names)))

        total_jd_skills = len(jd_skill_names)
        coverage_pct = round((len(matched) / total_jd_skills * 100), 1) if total_jd_skills > 0 else 0.0

        sim_score = self.nlp.compute_similarity(" ".join(student_skill_names), jd_text)
        readiness = round((coverage_pct * 0.7) + (sim_score * 100.0 * 0.3), 1)

        keywords = self.nlp.extract_keywords_from_jd(jd_text, top_n=10)

        # Gap items
        gap_items = []
        for s in missing:
            meta = self.skills_db.get(s, {})
            gap_items.append({
                "skill": s,
                "category": meta.get("category", "General"),
                "priority": "High" if meta.get("importance_weight", 1.0) > 1.3 else "Medium",
                "resources": meta.get("resources", []),
                "project_ideas": meta.get("project_ideas", [])
            })

        return {
            "total_jd_skills": total_jd_skills,
            "matched_skills": matched,
            "missing_skills": missing,
            "bonus_skills": bonus,
            "readiness_score": readiness,
            "nlp_similarity": round(sim_score * 100, 1),
            "key_terms": keywords,
            "gap_items": gap_items
        }

