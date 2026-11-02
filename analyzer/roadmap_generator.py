import math


class RoadmapGenerator:
    def __init__(self, skills_db: dict):
        self.skills_db = skills_db.get("skills", {})

    def generate_roadmap(self, gap_analysis: dict) -> dict:
        """
        Generates a tailored learning roadmap with timeline, phases,
        milestone projects, and interview preparation.
        """
        missing_core = gap_analysis.get("missing_core", [])
        missing_secondary = gap_analysis.get("missing_secondary", [])
        role_title = gap_analysis.get("role_title", "Target Role")

        total_gaps = len(missing_core) + len(missing_secondary)
        
        # Calculate estimated weeks (approx 1.5 weeks per core skill, 1 week per secondary)
        est_weeks = max(2, math.ceil(len(missing_core) * 1.5 + len(missing_secondary) * 0.8))
        est_hours = est_weeks * 12  # Assuming 12 hrs/week study time

        phases = []
        phase_num = 1

        # Phase 1: Core Fundamentals (High Priority Gaps)
        if missing_core:
            phase1_skills = []
            for s in missing_core:
                meta = self.skills_db.get(s, {})
                phase1_skills.append({
                    "skill": s,
                    "category": meta.get("category", "Core Technical"),
                    "resources": meta.get("resources", []),
                    "action_item": f"Master core syntax, design patterns, and foundational problems for {s}."
                })

            phases.append({
                "phase_index": phase_num,
                "title": f"Phase {phase_num}: Core Foundations & Essential Gaps",
                "duration": f"Weeks 1 - {max(2, math.ceil(len(missing_core) * 1.5))}",
                "focus": "Closing critical must-have skill gaps required by 90%+ job listings",
                "status": "In Progress",
                "skills": phase1_skills
            })
            phase_num += 1

        # Phase 2: Secondary Tools & Ecosystem
        if missing_secondary:
            phase2_skills = []
            for s in missing_secondary:
                meta = self.skills_db.get(s, {})
                phase2_skills.append({
                    "skill": s,
                    "category": meta.get("category", "Frameworks & Ecosystem"),
                    "resources": meta.get("resources", []),
                    "action_item": f"Understand industry workflows, deployment, and practical usage of {s}."
                })

            start_wk = phases[-1]["phase_index"] * 2 + 1 if phases else 1
            phases.append({
                "phase_index": phase_num,
                "title": f"Phase {phase_num}: Ecosystem, Tooling & Framework Mastery",
                "duration": f"Weeks {start_wk} - {start_wk + max(2, len(missing_secondary))}",
                "focus": "Secondary tools, production best practices, and integration",
                "status": "Upcoming",
                "skills": phase2_skills
            })
            phase_num += 1

        # Phase 3: Capstone Portfolio Project
        capstone_ideas = self._get_capstone_project(role_title, missing_core + gap_analysis.get("matched_core", []))
        phases.append({
            "phase_index": phase_num,
            "title": f"Phase {phase_num}: Capstone Project & Portfolio Build",
            "duration": f"Final 2 Weeks",
            "focus": "Build, document, and deploy a full-scale portfolio project to prove your readiness",
            "status": "Upcoming",
            "project_name": capstone_ideas["name"],
            "project_description": capstone_ideas["description"],
            "deliverables": capstone_ideas["deliverables"]
        })

        # Role-specific Mock Interview Questions
        interview_prep = self._get_interview_questions(role_title)

        return {
            "target_role": role_title,
            "estimated_weeks": est_weeks,
            "estimated_hours": est_hours,
            "total_gaps_addressed": total_gaps,
            "phases": phases,
            "interview_questions": interview_prep
        }

    def _get_capstone_project(self, role_title: str, skills_list: list) -> dict:
        """Suggests a prominent portfolio project tailored to the role."""
        role_lower = role_title.lower()
        if "data scientist" in role_lower or "analyst" in role_lower:
            return {
                "name": "End-to-End Market Sentiment & Predictive Churn Pipeline",
                "description": "Scrape social/customer feedback, conduct exploratory data analysis (EDA), engineer NLP features, build predictive churn classification models with Scikit-learn, and deploy an interactive Streamlit/Flask dashboard.",
                "deliverables": ["GitHub repository with clean README and modular code", "Live deployed web application", "Executive summary report with visual findings"]
            }
        elif "learning" in role_lower or "ai" in role_lower:
            return {
                "name": "Production Deep Learning / LLM RAG Assistant",
                "description": "Develop a Retrieval-Augmented Generation (RAG) assistant using vector embeddings, PyTorch/Transformers, Dockerized API backend, and automated model evaluation metrics.",
                "deliverables": ["Containerized Docker application", "Benchmark evaluation metrics table", "CI/CD automated testing pipeline"]
            }
        elif "devops" in role_lower or "cloud" in role_lower:
            return {
                "name": "Cloud-Native GitOps Microservices Cluster",
                "description": "Deploy a containerized microservices application onto Kubernetes, automated with GitHub Actions CI/CD pipelines, AWS infrastructure provisioned via Terraform, and Grafana monitoring.",
                "deliverables": ["Kubernetes manifest and Helm charts", "CI/CD workflow definitions", "Architecture diagram and stress test logs"]
            }
        else:
            return {
                "name": "Full-Stack Enterprise Workflow Management System",
                "description": "Build a responsive web application with JWT authentication, role-based access control, relational database storage, background job processing, and RESTful API endpoints.",
                "deliverables": ["Full-stack repository with API documentation", "Responsive frontend UI", "Unit and integration test suite"]
            }

    def _get_interview_questions(self, role_title: str) -> list:
        """Returns targeted interview prep questions based on the target role."""
        role_lower = role_title.lower()
        if "data" in role_lower or "analyst" in role_lower:
            return [
                {
                    "question": "How do you handle missing or skewed data before feeding it into a model?",
                    "key_points": "Mean/Median vs KNN imputation, log/box-cox transformation for skewness, identifying MAR vs MCAR mechanisms."
                },
                {
                    "question": "Explain the bias-variance tradeoff and how regularization (L1/L2) helps.",
                    "key_points": "High bias = underfitting, high variance = overfitting. L1 (Lasso) causes sparsity, L2 (Ridge) shrinks weights."
                },
                {
                    "question": "Can you explain the difference between WHERE and HAVING in SQL?",
                    "key_points": "WHERE filters rows before aggregation; HAVING filters aggregated groups after GROUP BY."
                }
            ]
        elif "ml" in role_lower or "ai" in role_lower:
            return [
                {
                    "question": "How do self-attention mechanisms in Transformers work?",
                    "key_points": "Query, Key, Value matrix projections, scaled dot-product attention softmax(QK^T / sqrt(d_k))V."
                },
                {
                    "question": "How do you monitor and resolve model drift and concept drift in production?",
                    "key_points": "Statistical checks (KS-test, PSI), ground-truth feedback loops, automated retraining pipelines."
                },
                {
                    "question": "Why do vanishing gradients happen and how do modern architectures solve it?",
                    "key_points": "Sigmoid/tanh derivatives < 0.25; solved using ReLU, residual connections (ResNet), and layer normalization."
                }
            ]
        elif "devops" in role_lower:
            return [
                {
                    "question": "Explain the difference between a Kubernetes Pod, Deployment, and Service.",
                    "key_points": "Pod is the atomic container wrapper; Deployment manages replica state and rolling updates; Service provides persistent IP and load balancing."
                },
                {
                    "question": "What is the 12-factor app methodology and why is it crucial for cloud deployments?",
                    "key_points": "Stateless processes, config in environment variables, port binding, disposable processes."
                }
            ]
        else:
            return [
                {
                    "question": "How does the JavaScript Event Loop handle asynchronous microtasks vs macrotasks?",
                    "key_points": "Call stack executes synchronous code; microtasks (Promises) execute immediately after the current frame before macrotasks (setTimeout)."
                },
                {
                    "question": "What are RESTful API best practices regarding HTTP status codes and idempotency?",
                    "key_points": "GET/PUT/DELETE are idempotent; POST creates resources; proper use of 200, 201, 400, 401, 403, 404, 500."
                },
                {
                    "question": "How do database indexes improve query speeds and what are their drawbacks?",
                    "key_points": "B-Tree lookups O(log N) instead of table scans O(N); overhead on write/insert/update operations and disk space."
                }
            ]

