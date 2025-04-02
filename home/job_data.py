import json
import os

DATA_FILE = "job_data.json"

# Predefined initial data
initial_data = {
    "Data Scientist": "machine learning, python, data analysis, statistics, big data, predictive modeling, data visualization, SQL, R, AI frameworks",
    "Software Engineer": "programming, software development, java, python, debugging, software architecture, version control, problem-solving, algorithms, data structures",
    "Project Manager": "project management, communication, leadership, planning, budgeting, scheduling, risk management, stakeholder management, Agile, Scrum",
    "Web Developer": "html, css, javascript, web development, responsive design, web performance, React, Angular, frontend frameworks, REST APIs",
    "System Administrator": "networking, system management, troubleshooting, linux, server maintenance, scripting, security protocols, virtualization, cloud services",
    "UX Designer": "user experience, design thinking, prototyping, wireframing, user research, usability testing, interaction design, visual design, Figma, Adobe XD",
    "Business Analyst": "data analysis, requirements gathering, problem solving, communication, stakeholder engagement, documentation, process improvement, SQL, visualization tools",
    "Cybersecurity Specialist": "cybersecurity, network security, risk assessment, cryptography, ethical hacking, incident response, firewalls, penetration testing, security audits",
    "Cloud Engineer": "cloud computing, aws, azure, cloud architecture, containerization, Kubernetes, cloud security, serverless computing, cost optimization",
    "AI Engineer": "artificial intelligence, deep learning, machine learning, python, neural networks, TensorFlow, PyTorch, NLP, computer vision, AI ethics",
    "DevOps Engineer": "devops, ci/cd, automation, containerization, Docker, Kubernetes, cloud platforms, infrastructure as code, monitoring, scripting",
    "Database Administrator": "database management, sql, nosql, data modeling, database security, performance tuning, backup and recovery, Oracle, MySQL, PostgreSQL",
    "Digital Marketing Specialist": "seo, social media, content marketing, google analytics, PPC campaigns, email marketing, keyword research, brand strategy, data analysis",
    "Product Manager": "product lifecycle management, roadmap planning, customer research, agile methodologies, UX/UI principles, stakeholder communication, competitive analysis",
    "Electrical Engineer": "circuit design, power systems, plc programming, embedded systems, signal processing, renewable energy systems, MATLAB, PCB design, IoT devices",
    "Civil Engineer": "construction management, structural analysis, autocad, surveying, project planning, cost estimation, geotechnical engineering, sustainability",
    "Content Writer": "copywriting, content creation, seo writing, storytelling, grammar, editing, research, creative writing, content strategy, audience engagement",
    "Human Resources Specialist": "recruitment, employee relations, training, hr policies, conflict resolution, performance management, payroll systems, compliance, organizational development",
    "Graphic Designer": "adobe photoshop, adobe illustrator, typography, branding, color theory, layout design, visual storytelling, print design, digital media, creativity",
    "Teacher": "teaching, curriculum development, classroom management, communication, lesson planning, student assessment, subject expertise, online teaching tools, mentoring",

}

# Load existing data or create a new file with initial data
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as file:
        existing_data = json.load(file)
else:
    existing_data = {}

# Merge initial data with existing data (existing data takes priority)
data = {**initial_data, **existing_data}

# Save merged data back to file
with open(DATA_FILE, "w") as file:
    json.dump(data, file, indent=4)

# Function to save data to file
def save_data():
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)
