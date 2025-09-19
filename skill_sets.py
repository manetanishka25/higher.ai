# skill_sets.py
# Keep these short; expand for your domain.
CANONICAL_SKILLS = sorted(set([
    # Core
    "Python", "Java", "JavaScript", "TypeScript", "Go", "C++", "C#", "SQL", "NoSQL",
    "HTML", "CSS", "React", "Node.js", "Express", "Next.js", "Django", "Flask", "FastAPI",
    "Spring", "Kubernetes", "Docker", "AWS", "GCP", "Azure", "Terraform",
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "Kafka", "Spark", "Hadoop",
    "Airflow", "Tableau", "Power BI", "Figma",
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "PyTorch", "TensorFlow",
    "Git", "CI/CD", "REST", "GraphQL", "gRPC",
    # Data/Analytics
    "Pandas", "NumPy", "scikit-learn",
    # QA/Testing
    "Selenium", "Playwright", "Cypress", "JUnit", "pytest",
    # Mobile
    "Android", "iOS", "Swift", "Kotlin", "React Native", "Flutter",
    # DevOps/SRE
    "Linux", "Prometheus", "Grafana",
    # Security
    "OWASP", "Threat Modeling",
    # Product/PM
    "Jira", "A/B Testing",
]))

SKILL_GROUPS = {
    "Languages": ["Python", "Java", "JavaScript", "TypeScript", "Go", "C++", "C#", "SQL"],
    "Frontend": ["React", "HTML", "CSS", "Next.js"],
    "Backend": ["Node.js", "Express", "Django", "Flask", "FastAPI", "Spring", "GraphQL", "gRPC", "REST"],
    "Data": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Kafka", "Spark", "Airflow", "Pandas", "NumPy", "scikit-learn"],
    "ML": ["Machine Learning", "Deep Learning", "NLP", "Computer Vision", "PyTorch", "TensorFlow"],
    "DevOps": ["Docker", "Kubernetes", "AWS", "GCP", "Azure", "Terraform", "Linux", "CI/CD", "Prometheus", "Grafana"],
    "Testing": ["Selenium", "Playwright", "Cypress", "JUnit", "pytest"],
    "Mobile": ["Android", "iOS", "Swift", "Kotlin", "React Native", "Flutter"],
    "Analytics/BI": ["Tableau", "Power BI"],
    "Design": ["Figma"],
    "Security": ["OWASP", "Threat Modeling"],
    "Product": ["Jira", "A/B Testing"],
}

LANGUAGES = [
    "English", "Hindi", "French", "German", "Spanish", "Italian", "Mandarin", "Japanese", "Korean",
]
