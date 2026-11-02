import re


class ATSScorer:
    """
    Evaluates Resume / Profile text for Applicant Tracking System (ATS) friendliness,
    structure completeness, action verb density, quantifiable business impact,
    and weak verb replacement detection.
    """

    ACTION_VERBS = {
        "spearheaded", "architected", "engineered", "implemented", "developed",
        "designed", "deployed", "optimized", "streamlined", "automated",
        "orchestrated", "constructed", "facilitated", "integrated", "leveraged",
        "accelerated", "maximized", "transformed", "formulated", "executed",
        "supervised", "collaborated", "managed", "reduced", "increased"
    }

    REQUIRED_SECTIONS = [
        ("summary", r"(?:summary|objective|about\s+me|profile)", "Professional Summary / Objective"),
        ("skills", r"(?:technical\s+skills|skills|technologies|proficiencies|core\s+competencies)", "Technical Skills Section"),
        ("experience", r"(?:experience|work\s+history|employment|internships|work\s+experience)", "Work / Internship Experience"),
        ("projects", r"(?:projects|academic\s+projects|personal\s+projects)", "Hands-On Projects"),
        ("education", r"(?:education|academic\s+background|qualifications|academics)", "Education & Credentials")
    ]

    WEAK_VERBS_MAP = {
        "worked on": {
            "replacements": ["Architected", "Engineered", "Spearheaded", "Constructed"],
            "reason": "Passive phrase that doesn't convey technical ownership or scale."
        },
        "working on": {
            "replacements": ["Engineering", "Architecting", "Deploying", "Pioneering"],
            "reason": "Conveys ongoing effort rather than concrete completed milestone."
        },
        "responsible for": {
            "replacements": ["Orchestrated", "Directed", "Executed", "Administered"],
            "reason": "Sounds like a job description duty rather than candidate achievement."
        },
        "helped with": {
            "replacements": ["Co-engineered", "Collaborated on", "Facilitated", "Accelerated"],
            "reason": "Minimizes your contribution; use active co-development terms."
        },
        "assisted with": {
            "replacements": ["Co-developed", "Facilitated", "Streamlined", "Accelerated"],
            "reason": "Downplays technical competency."
        },
        "handled": {
            "replacements": ["Administered", "Streamlined", "Standardized", "Maintained"],
            "reason": "Vague verb; specify engineering or administrative impact."
        },
        "did": {
            "replacements": ["Executed", "Implemented", "Authored", "Formulated"],
            "reason": "Colloquial and non-descriptive."
        },
        "made": {
            "replacements": ["Developed", "Constructed", "Authored", "Pioneered"],
            "reason": "Generic; specify exact technical action."
        },
        "created": {
            "replacements": ["Architected", "Engineered", "Designed & Built", "Pioneered"],
            "reason": "Can be elevated to show senior system design capability."
        },
        "tested": {
            "replacements": ["Validated", "Benchmarked", "Audited", "Rigidly Tested"],
            "reason": "Specify testing methodology like benchmarking or rigorous validation."
        },
        "fixed": {
            "replacements": ["Resolved", "Refactored", "Optimized", "Remediated"],
            "reason": "Use engineering terms like refactored or remediated."
        },
        "learned": {
            "replacements": ["Mastered", "Adopted", "Assimilated"],
            "reason": "Elevate learning into active professional mastery."
        }
    }

    POWER_VERB_CATEGORIES = {
        "Engineering & Architecture": [
            {"verb": "Architected", "example": "Architected modular microservices handling 50k requests/min."},
            {"verb": "Engineered", "example": "Engineered automated data ingestion pipeline using Python & SQL."},
            {"verb": "Constructed", "example": "Constructed end-to-end RESTful API endpoints with JWT auth."},
            {"verb": "Deployed", "example": "Deployed containerized applications with automated CI/CD checks."}
        ],
        "Performance & Optimization": [
            {"verb": "Optimized", "example": "Optimized SQL database query indexes, cutting query latency by 42%."},
            {"verb": "Accelerated", "example": "Accelerated model training pipeline throughput by 3x."},
            {"verb": "Streamlined", "example": "Streamlined developer test cycles from 45 mins to 12 mins."},
            {"verb": "Maximized", "example": "Maximized resource utilization, lowering server costs by 20%."}
        ],
        "Leadership & Initiative": [
            {"verb": "Spearheaded", "example": "Spearheaded technical migration from legacy backend to Flask APIs."},
            {"verb": "Pioneered", "example": "Pioneered unit testing culture, raising code test coverage to 88%."},
            {"verb": "Orchestrated", "example": "Orchestrated cross-functional release sprints with zero production regression."}
        ],
        "Automation & Intelligence": [
            {"verb": "Automated", "example": "Automated weekly reporting pipelines, saving 15 manual engineering hours/week."},
            {"verb": "Synthesized", "example": "Synthesized large-scale datasets into interactive executive dashboards."},
            {"verb": "Extracted", "example": "Extracted high-signal market features using advanced web scrapers."}
        ]
    }

    def __init__(self):
        pass

    def evaluate(self, raw_text: str, detected_skills_count: int = 0) -> dict:
        """
        Calculates ATS compatibility score (0-100), detects weak phrases,
        and produces actionable feedback with power verb suggestions.
        """
        if not raw_text or len(raw_text.strip()) < 50:
            return {
                "overall_score": 20,
                "tier": "Poor",
                "tier_badge": "danger",
                "word_count": len(raw_text.split()) if raw_text else 0,
                "metrics_detected": 0,
                "action_verbs_found": [],
                "missing_sections": ["Experience", "Projects", "Skills", "Education"],
                "present_sections": [],
                "weak_phrases_detected": [],
                "power_verb_categories": self.POWER_VERB_CATEGORIES,
                "suggestions": [
                    "Resume text is too brief. Standard tech resumes should contain at least 250 - 600 words.",
                    "Include distinct section headings for Technical Skills, Projects, and Education."
                ]
            }

        text_lower = raw_text.lower()
        words = re.findall(r"\b[a-zA-Z0-9_-]+\b", text_lower)
        word_count = len(words)

        # 1. Section Completeness Check (Weight: 30%)
        present_sections = []
        missing_sections = []
        for key, pattern, label in self.REQUIRED_SECTIONS:
            if re.search(rf"(?:^|\n)[\s#*\-_]*{pattern}[:\s]*", text_lower, re.MULTILINE):
                present_sections.append(label)
            else:
                missing_sections.append(label)

        section_score = (len(present_sections) / len(self.REQUIRED_SECTIONS)) * 30.0

        # 2. Action Verbs Check (Weight: 25%)
        found_verbs = set()
        for w in words:
            if w in self.ACTION_VERBS:
                found_verbs.add(w.capitalize())

        # Target: At least 5 distinct high-impact action verbs
        verb_ratio = min(1.0, len(found_verbs) / 5.0)
        verb_score = verb_ratio * 25.0

        # 3. Quantifiable Impact & Metrics Check (Weight: 25%)
        metric_matches = re.findall(r"(?:\d+(?:\.\d+)?%\b|\$\d+|\b\d+\s*(?:k|m|users|requests|records|teams|lpa|fps|ms|gb|tb)\b|\b\d{2,}\b)", raw_text, re.IGNORECASE)
        metric_count = len(metric_matches)
        metric_ratio = min(1.0, metric_count / 4.0)
        metric_score = metric_ratio * 25.0

        # 4. Length & Formatting Score (Weight: 20%)
        length_score = 0.0
        if 250 <= word_count <= 800:
            length_score = 20.0
        elif 150 <= word_count < 250 or 800 < word_count <= 1200:
            length_score = 14.0
        else:
            length_score = 8.0

        # Overall ATS Score (0 - 100)
        total_ats = round(section_score + verb_score + metric_score + length_score, 1)
        total_ats = min(100.0, max(15.0, total_ats))

        if total_ats >= 80:
            tier = "Excellent (ATS Ready)"
            tier_badge = "success"
        elif total_ats >= 65:
            tier = "Good (Minor Fixes Needed)"
            tier_badge = "primary"
        elif total_ats >= 50:
            tier = "Average (Needs Polish)"
            tier_badge = "warning"
        else:
            tier = "Needs Significant Improvement"
            tier_badge = "danger"

        # 5. Detect Weak / Passive Phrases in candidate resume lines
        weak_phrases_detected = []
        raw_lines = [line.strip().strip("-•* ") for line in raw_text.split("\n") if line.strip()]
        seen_weak = set()

        for line in raw_lines:
            line_lower = line.lower()
            for weak_phrase, meta in self.WEAK_VERBS_MAP.items():
                pattern = rf"\b{re.escape(weak_phrase)}\b"
                if re.search(pattern, line_lower):
                    key = (weak_phrase, line)
                    if key in seen_weak:
                        continue
                    seen_weak.add(key)

                    replacement = meta["replacements"][0]
                    # Substitute weak phrase with power verb
                    enhanced_bullet = re.sub(pattern, replacement, line, count=1, flags=re.IGNORECASE)
                    
                    weak_phrases_detected.append({
                        "weak_phrase": weak_phrase,
                        "original_line": line[:110] + ("..." if len(line) > 110 else ""),
                        "power_replacements": meta["replacements"],
                        "reason": meta["reason"],
                        "enhanced_preview": enhanced_bullet[:130] + ("..." if len(enhanced_bullet) > 130 else "")
                    })
                    break  # One match per line

        # Generate Actionable Suggestions
        suggestions = []
        if missing_sections:
            suggestions.append(f"Add missing ATS section headings: {', '.join(missing_sections)}.")
        if len(found_verbs) < 4:
            suggestions.append("Start bullet points with powerful action verbs like 'Engineered', 'Optimized', 'Architected' rather than passive phrases like 'Responsible for' or 'Helped with'.")
        if weak_phrases_detected:
            suggestions.append(f"Found {len(weak_phrases_detected)} passive phrase(s) like '{weak_phrases_detected[0]['weak_phrase']}'. Use the Power Verb Swapper below to replace them.")
        if metric_count < 3:
            suggestions.append("Add quantifiable metrics to your project achievements (e.g., 'reduced API latency by 35%', 'processed 50k records', 'scaled to 500 active users').")
        if word_count < 300:
            suggestions.append("Expand on your technical projects and internship responsibilities. Aim for 350-600 words.")
        elif word_count > 900:
            suggestions.append("Your resume may be too long for an early-career candidate. Aim to keep it under 800 words (1-2 pages maximum).")
        if detected_skills_count < 6:
            suggestions.append("Explicitly list industry-standard technical tools, programming languages, and frameworks in a dedicated 'Skills' section.")

        return {
            "overall_score": total_ats,
            "tier": tier,
            "tier_badge": tier_badge,
            "word_count": word_count,
            "metrics_detected": metric_count,
            "metrics_examples": metric_matches[:5],
            "action_verbs_found": sorted(list(found_verbs)),
            "action_verb_count": len(found_verbs),
            "present_sections": present_sections,
            "missing_sections": missing_sections,
            "weak_phrases_detected": weak_phrases_detected[:6],
            "power_verb_categories": self.POWER_VERB_CATEGORIES,
            "subscores": {
                "sections": round(section_score, 1),
                "action_verbs": round(verb_score, 1),
                "quantifiable_impact": round(metric_score, 1),
                "length_format": round(length_score, 1)
            },
            "suggestions": suggestions
        }

    def polish_bullet(self, raw_bullet: str, target_skill: str = "") -> dict:
        """
        Transforms any raw or weak bullet point into 3 high-impact,
        STAR-method recruiter-ready bullet points.
        """
        cleaned = raw_bullet.strip().strip("-•* ")
        if not cleaned:
            cleaned = "Built web application using Python and database queries"

        skill = target_skill.strip() if target_skill else "modern tech stack"

        detected_weak = None
        for weak_p in self.WEAK_VERBS_MAP:
            if re.search(rf"\b{re.escape(weak_p)}\b", cleaned, re.IGNORECASE):
                detected_weak = weak_p
                break

        # Clean leading words if passive
        topic = cleaned
        for weak_p in self.WEAK_VERBS_MAP:
            topic = re.sub(rf"^(?:i\s+|we\s+)?{re.escape(weak_p)}\s*", "", topic, flags=re.IGNORECASE).strip()

        if not topic or len(topic) < 4:
            topic = "backend data processing workflows"

        variations = [
            {
                "type": "Performance & Optimization",
                "badge": "success",
                "power_verb": "Optimized",
                "text": f"Optimized and enhanced {topic} using {skill}, reducing system execution latency by 35% and improving uptime.",
                "metric_added": "35% latency reduction"
            },
            {
                "type": "Architecture & Scale",
                "badge": "primary",
                "power_verb": "Architected",
                "text": f"Architected and deployed {topic} utilizing {skill}, reliably processing 10,000+ daily requests with zero downtime.",
                "metric_added": "10k+ daily transactions & 99.9% uptime"
            },
            {
                "type": "Automation & Pipeline Throughput",
                "badge": "warning",
                "power_verb": "Spearheaded",
                "text": f"Spearheaded development of automated {topic} leveraging {skill}, accelerating end-to-end throughput by 42%.",
                "metric_added": "42% throughput acceleration"
            }
        ]

        return {
            "original": cleaned,
            "detected_weak_verb": detected_weak,
            "variations": variations
        }
