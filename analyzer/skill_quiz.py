"""
Interactive Skill Diagnostic Quiz Engine.
Provides bite-sized competency check questions for key technical skills.
"""


class SkillQuizEngine:
    QUIZ_DATABASE = {
        "Python": [
            {
                "question": "What is the primary difference between a Python list and a tuple?",
                "options": [
                    "Lists are mutable while tuples are immutable",
                    "Tuples can only hold integers while lists hold any type",
                    "Lists use parentheses while tuples use square brackets",
                    "Tuples cannot be indexed or iterated"
                ],
                "correct_index": 0,
                "explanation": "Lists can be modified after creation (mutable), whereas tuples cannot be changed once defined (immutable)."
            },
            {
                "question": "In Python, which built-in function or syntax is used to create a generator?",
                "options": [
                    "The 'yield' keyword inside a function",
                    "The 'generate' keyword",
                    "The list() constructor",
                    "The @generator decorator"
                ],
                "correct_index": 0,
                "explanation": "A generator function uses the 'yield' keyword to produce values lazily one at a time on demand."
            },
            {
                "question": "What is the time complexity of searching for a key in a Python dictionary on average?",
                "options": [
                    "O(1) constant time",
                    "O(N) linear time",
                    "O(log N) logarithmic time",
                    "O(N^2) quadratic time"
                ],
                "correct_index": 0,
                "explanation": "Python dictionaries are implemented as hash tables, providing O(1) average lookup time."
            }
        ],
        "SQL": [
            {
                "question": "What is the key difference between INNER JOIN and LEFT JOIN?",
                "options": [
                    "INNER JOIN returns only matching rows; LEFT JOIN returns all rows from the left table plus matching rows from the right",
                    "LEFT JOIN deletes unlinked records",
                    "INNER JOIN works only on numeric foreign keys",
                    "LEFT JOIN can only join two tables, not three"
                ],
                "correct_index": 0,
                "explanation": "LEFT JOIN keeps all rows from the left table, filling unmatched right table columns with NULL."
            },
            {
                "question": "Which clause is used to filter records after aggregate functions (like SUM, COUNT, AVG) have been calculated?",
                "options": [
                    "HAVING",
                    "WHERE",
                    "FILTER BY",
                    "GROUP FILTER"
                ],
                "correct_index": 0,
                "explanation": "WHERE filters rows before aggregation; HAVING filters groups after aggregation."
            },
            {
                "question": "What is an index in a relational database primarily used for?",
                "options": [
                    "Speeding up data retrieval at the cost of slower writes and additional storage",
                    "Encrypting sensitive table columns",
                    "Enforcing primary key uniqueness only",
                    "Compressing text columns"
                ],
                "correct_index": 0,
                "explanation": "Indexes (like B-trees) accelerate SELECT queries dramatically while introducing write overhead."
            }
        ],
        "React": [
            {
                "question": "What hook in React is used to perform side effects such as fetching data or setting timers?",
                "options": [
                    "useEffect",
                    "useState",
                    "useMemo",
                    "useReducer"
                ],
                "correct_index": 0,
                "explanation": "useEffect lets you synchronize a component with external systems (APIs, DOM events, timers)."
            },
            {
                "question": "Why should you avoid directly modifying the state variable in React (e.g. state.count = 5)?",
                "options": [
                    "Direct mutation does not trigger a component re-render",
                    "It will crash JavaScript immediately with a SyntaxError",
                    "React state variables are read-only constants by JavaScript definition",
                    "It breaks CSS styling"
                ],
                "correct_index": 0,
                "explanation": "React relies on state setters to schedule re-rendering and reconcile the virtual DOM."
            },
            {
                "question": "What is the purpose of the 'key' prop when rendering lists of elements in React?",
                "options": [
                    "Helps React identify which items have changed, been added, or been removed",
                    "Assigns an HTML id to each rendered item",
                    "Encrypts component state",
                    "Binds click events to each element"
                ],
                "correct_index": 0,
                "explanation": "Keys give elements a stable identity so React can efficiently reorder and diff DOM nodes."
            }
        ],
        "Machine Learning": [
            {
                "question": "What does a high training accuracy combined with a low validation/test accuracy typically indicate?",
                "options": [
                    "Overfitting (High Variance)",
                    "Underfitting (High Bias)",
                    "Data Leakage into Test Set",
                    "Optimal model performance"
                ],
                "correct_index": 0,
                "explanation": "Overfitting occurs when a model memorizes the training data but fails to generalize to unseen data."
            },
            {
                "question": "Which evaluation metric is best suited for an imbalanced classification problem (e.g., fraud detection with 99.9% negative class)?",
                "options": [
                    "F1-Score / PR-AUC",
                    "Raw Accuracy",
                    "Mean Squared Error (MSE)",
                    "R-Squared"
                ],
                "correct_index": 0,
                "explanation": "Raw accuracy can be misleading (e.g. 99.9% by predicting only the majority class), whereas F1-Score balances Precision and Recall."
            },
            {
                "question": "What is the primary difference between L1 (Lasso) and L2 (Ridge) regularization?",
                "options": [
                    "L1 can shrink feature weights to exactly zero (feature selection), while L2 shrinks weights close to zero",
                    "L2 eliminates unimportant features completely",
                    "L1 is only used in unsupervised learning",
                    "L2 is computationally impossible for large matrices"
                ],
                "correct_index": 0,
                "explanation": "L1 norm induces sparsity by forcing coefficients of uninformative features to zero."
            }
        ],
        "Docker": [
            {
                "question": "What is the difference between a Docker Image and a Docker Container?",
                "options": [
                    "An image is a read-only template; a container is a running instance of an image",
                    "A container is a read-only blueprint; an image is the running process",
                    "Images run on Linux; containers run only on Windows",
                    "There is no difference; the terms are synonymous"
                ],
                "correct_index": 0,
                "explanation": "A Docker image contains application code, runtime, and libraries. Containers are running, isolated instances of that image."
            },
            {
                "question": "What does the 'EXPOSE' directive in a Dockerfile do?",
                "options": [
                    "Documents which network ports the container listens on, without publishing them automatically to the host",
                    "Automatically routes public internet traffic to the container",
                    "Opens the host machine firewall",
                    "Sets environment variables"
                ],
                "correct_index": 0,
                "explanation": "EXPOSE acts as documentation between the image author and user; host publishing requires -p or -P at runtime."
            },
            {
                "question": "Why is multi-stage building used in modern Dockerfiles?",
                "options": [
                    "To produce much smaller, secure production images by discarding build tools and intermediate artifacts",
                    "To run multiple containers simultaneously from one file",
                    "To bypass Docker image cache",
                    "To run both Python and Node.js in the same process"
                ],
                "correct_index": 0,
                "explanation": "Multi-stage builds allow you to compile assets in a heavy builder stage and copy only binaries into a lean runtime image."
            }
        ]
    }

    def get_quiz_for_skill(self, skill_name: str) -> dict:
        """Returns diagnostic questions for a skill, or fallback questions if not directly indexed."""
        # Find exact or case-insensitive match
        for key in self.QUIZ_DATABASE:
            if key.lower() == skill_name.lower():
                return {
                    "skill": key,
                    "available": True,
                    "questions": self.QUIZ_DATABASE[key]
                }

        # Fallback generic technical assessment questions
        return {
            "skill": skill_name,
            "available": True,
            "questions": [
                {
                    "question": f"When implementing {skill_name} in a production environment, what is the best practice for configuration management?",
                    "options": [
                        "Use environment variables and secret managers rather than hardcoded credentials",
                        "Hardcode configuration strings directly into source control",
                        "Store all credentials in public git repositories",
                        "Disable logging and monitoring"
                    ],
                    "correct_index": 0,
                    "explanation": "Industry 12-factor standard requires separating configuration/secrets from code using environment variables."
                },
                {
                    "question": f"How should errors and exceptions typically be handled when working with {skill_name}?",
                    "options": [
                        "Catch specific exceptions, log diagnostic contexts, and provide meaningful fallback messages",
                        "Wrap entire applications in blank 'catch-all' blocks that suppress errors silently",
                        "Allow applications to crash without any logging",
                        "Avoid testing or validating user inputs"
                    ],
                    "correct_index": 0,
                    "explanation": "Robust error handling requires specific exception handling, contextual logging, and graceful degradation."
                },
                {
                    "question": f"What is a critical performance consideration when scaling systems that rely on {skill_name}?",
                    "options": [
                        "Caching frequent queries, optimizing I/O bottlenecks, and monitoring latency percentiles (p95/p99)",
                        "Increasing server memory without indexing or optimizing algorithms",
                        "Ignoring network serialization costs",
                        "Disabling connection pooling"
                    ],
                    "correct_index": 0,
                    "explanation": "High-throughput architectures optimize I/O, utilize caching, connection pooling, and monitor tail latency."
                }
            ]
        }

