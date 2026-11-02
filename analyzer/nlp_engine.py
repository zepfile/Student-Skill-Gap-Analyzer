import re
import math
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class NLPEngine:
    def __init__(self, skills_db: dict):
        """
        Initializes the NLP engine with the standardized skills database.
        """
        if isinstance(skills_db, dict) and "skills" in skills_db:
            self.skills_db = skills_db["skills"]
        elif isinstance(skills_db, dict):
            self.skills_db = skills_db
        else:
            self.skills_db = {}
        self.alias_to_canonical = {}
        self._build_alias_index()

    @staticmethod
    def _normalize_token(text: str) -> str:
        """Standardizes hyphens, underscores, and extra whitespace."""
        t = text.lower()
        t = re.sub(r"[\-_/]", " ", t)
        return " ".join(t.split())

    def _build_alias_index(self):
        """Builds a mapping from lowercase aliases/variants to the canonical skill name."""
        # Built-in aliases for canonical tech skills
        common_aliases = {
            "Data Structures and Algorithms": ["data structures", "algorithms", "dsa", "data structures & algorithms", "data structure and algorithm"],
            "Testing and Debugging": ["testing", "debugging", "unit testing", "unittest", "pytest", "test driven development", "tdd"],
            "REST APIs": ["rest api", "restful", "restful api", "restful apis", "api", "apis", "api development"],
            "OOP": ["oops", "object oriented programming", "object-oriented programming", "object oriented"],
            "HTML": ["html5"],
            "CSS": ["css3", "bootstrap", "tailwind"],
            "JavaScript": ["js", "es6", "vanilla js", "ecmascript"],
            "Excel": ["ms excel", "microsoft excel", "spreadsheets", "advanced excel"],
            "Data Visualization": ["data viz", "matplotlib", "seaborn", "tableau", "power bi", "plotly"],
            "SQL": ["mysql", "postgresql", "postgres", "sqlite", "plsql", "t-sql", "relational database"],
            "Git": ["github", "gitlab", "version control", "git & github"],
            "Python": ["python3", "py"],
            "Java": ["core java", "java 8", "java 11", "java 17"],
            "Flask": ["flask api", "flask framework"],
            "Pandas": ["pandas library"]
        }

        for canonical_name, data in self.skills_db.items():
            variants = [canonical_name] + data.get("aliases", []) + common_aliases.get(canonical_name, [])
            for alias in variants:
                alias_clean = alias.strip().lower()
                self.alias_to_canonical[alias_clean] = canonical_name
                # Also index normalized version with hyphens as spaces
                norm_variant = self._normalize_token(alias_clean)
                if norm_variant:
                    self.alias_to_canonical[norm_variant] = canonical_name

    @staticmethod
    def clean_text(text: str) -> str:
        """Cleans and standardizes raw text."""
        if not text:
            return ""
        text = text.replace("\r", " ").replace("\n", " ")
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", " ", text)
        return " ".join(text.split())

    def extract_contact_info(self, text: str) -> dict:
        """Extracts candidate contact details like email, phone, and profile links."""
        info = {
            "email": None,
            "phone": None,
            "github": None,
            "linkedin": None,
            "portfolio": None
        }

        # Email Regex
        email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
        if email_match:
            info["email"] = email_match.group(0)

        # Phone Regex
        phone_match = re.search(r"(?:(?:\+|0{0,2})91[\s-]?)?[6789]\d{9}|(?:\+?1[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}", text)
        if phone_match:
            info["phone"] = phone_match.group(0).strip()

        # GitHub
        github_match = re.search(r"(?:https?:\/\/)?(?:www\.)?github\.com\/([a-zA-Z0-9_-]+)", text, re.IGNORECASE)
        if github_match:
            info["github"] = f"https://github.com/{github_match.group(1)}"

        # LinkedIn
        linkedin_match = re.search(r"(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/([a-zA-Z0-9_-]+)", text, re.IGNORECASE)
        if linkedin_match:
            info["linkedin"] = f"https://linkedin.com/in/{linkedin_match.group(1)}"

        return info

    def extract_skills(self, text: str) -> list:
        """
        Extracts skills from text using robust boundary matching,
        mapping back to canonical skill representations.
        """
        text_lower = f" {text.lower()} "
        # Normalized text where common delimiters and hyphens become spaces
        normalized = re.sub(r"[/,;:()|\n\r\t•·\-\[\]]", " ", text_lower)
        normalized = f" {' '.join(normalized.split())} "

        matched_canonical = set()

        # Sort aliases by length descending so longer phrases match first (e.g. 'machine learning' before 'machine')
        sorted_aliases = sorted(self.alias_to_canonical.keys(), key=lambda x: len(x), reverse=True)

        for alias in sorted_aliases:
            escaped_alias = re.escape(alias)
            # Match either as exact word boundary or with spaces
            pattern = rf"(?:^|\s|\b){escaped_alias}(?:\b|\s|$)"
            if re.search(pattern, normalized) or re.search(pattern, text_lower):
                canonical = self.alias_to_canonical[alias]
                matched_canonical.add(canonical)

        # Build list of detailed skill records
        extracted = []
        for skill_name in sorted(matched_canonical):
            meta = self.skills_db.get(skill_name, {})
            extracted.append({
                "name": skill_name,
                "category": meta.get("category", "General"),
                "importance_weight": meta.get("importance_weight", 1.0)
            })

        return extracted

    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Computes cosine similarity between two text corpuses using TF-IDF.
        Returns a score between 0.0 and 1.0.
        """
        if not text1 or not text2:
            return 0.0
        try:
            vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(round(sim, 3))
        except Exception:
            return 0.0

    def extract_keywords_from_jd(self, jd_text: str, top_n: int = 12) -> list:
        """
        Extracts salient keyword terms from a custom Job Description using TF-IDF.
        """
        if not jd_text or len(jd_text.strip()) < 20:
            return []
        try:
            vectorizer = TfidfVectorizer(stop_words='english', max_features=top_n * 2, ngram_range=(1, 2))
            matrix = vectorizer.fit_transform([jd_text])
            feature_names = vectorizer.get_feature_names_out()
            scores = matrix.toarray()[0]
            sorted_idx = scores.argsort()[::-1]
            keywords = [feature_names[i] for i in sorted_idx[:top_n] if len(feature_names[i]) > 2]
            return keywords
        except Exception:
            return []
