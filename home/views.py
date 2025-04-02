from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render


from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import PyPDF2 

from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import PyPDF2
import pytesseract
from PIL import Image
import os



from django.shortcuts import render, redirect
from django.db import connection  # To interact with MySQL
from django.contrib import messages
from django.contrib.auth.hashers import check_password  # For password hashing



import string 

# Your home view to handle the file upload and text extraction
"""def home(request):
    context = {}

    if request.method == "POST" and request.FILES.get("resume"):
        uploaded_file = request.FILES["resume"]

        # Save the uploaded file temporarily
        fs = FileSystemStorage()
        file_path = fs.save(uploaded_file.name, uploaded_file)
        file_path = fs.path(file_path)

        # Check the file type and process accordingly
        if uploaded_file.name.endswith('.pdf'):
            # Process the uploaded PDF file
            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
            context["resume_text"] = text
        elif uploaded_file.name.lower().endswith(('.png', '.jpg', '.jpeg')):
            # Process the uploaded image file using pytesseract
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img)
            context["resume_text"] = text
        else:
            context["error"] = "Please upload a valid PDF or image file (PNG, JPG, JPEG)."

        # Delete the file after processing (optional)
        fs.delete(file_path)

    return render(request, "project test 1.html", context)"""



from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect

# def login_view(request):
#     if request.method == "POST":
#         username = request.POST.get("username")
#         password = request.POST.get("password")

#         # Authenticate user using Django's built-in method
#         user = authenticate(request, username=username, password=password)

#         if user is not None:
#             # Log in the user
#             login(request, user)
#             messages.success(request, "Login successful!")
#             return redirect('afterlogin')  # Redirect to home or dashboard
#         else:
#             # Invalid login attempt
#             messages.error(request, "Invalid username or password.")
    
#     return render(request, "login.html")


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if username=='admin':
                return redirect('review_queue')
            else:
                return redirect('afterlogin')  # Replace 'home' with your desired redirect URL
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')




from django.shortcuts import render

def home_view(request):
    return render(request, 'project test 1.html')



"""from django.shortcuts import render

def signup_view(request):
    return render(request, 'signup.html')"""



from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import SignupForm

def signup_view(request):
    

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            # Create the new user
            user = form.save(commit=False)  # Don't save yet
            user.set_password(form.cleaned_data['password'])  # Hash the password
            user.save()  # Save the user to the database

            # Optionally, log the user in after signup (if desired)
            from django.contrib.auth import login
            login(request, user)

            messages.success(request, 'Account created successfully! You are now logged in.')
            return redirect('afterlogin')  # Redirect to home or dashboard
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})









from django.shortcuts import render
from django.http import HttpResponse
from .forms import FileUploadForm
import gensim
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import string
import numpy as np
import os

# Ensure necessary NLTK data files are downloaded
nltk.download('punkt')
nltk.download('stopwords')

# Your document text (template document)
document_text = """Rose Mariya Paul
System and Application Services Associate
rosemariya156@gmail.com
8943110333
Thrissur,Kerala
linkedin.com/in/rose-mariya-paul
Profile
Determined computer science student dedicated to driving company success through creative
problem-solving and innovative solutions. Eager to contribute to growth and competitiveness
while advancing skills and knowledge in the field.
Internship Experience
CodeAlpha, Web Developer Intern
Developed multiple projects utilizing HTML, CSS, and JavaScript,
demonstrating proficiency in front-end web development.07/2024
Education
BSc Computer Science
St Thomas College(Autonomous),Thrissur2022 – present
Higher Secondary
Sacred Heart CGHSS Thrissur
Completed 12th grade with a specialization in Commerce, achieving a
percentage of 99%.2020 – 2022
Class X
Sacred Heart CGHSS Thrissur
Completed 10th grade with 9 A+ grades in SSLC examination.2019 – 2020
Skills
•HTML,CSS,JS
•Python
•C Programming
•DBMS,SQL
•Problem Solving
Certificates
Python Full Stack Development
St Thomas College(Autonomous),Thrissur
Covered topics: Front-end Development with HTML, CSS, JavaScript and
Back-end Development with Python.04/2023Digital Skills:Artificial Intelligance
Accenture(in association with future learn)
Enhanced understanding of AI with interesting facts,trends and insights
and helped to explore working relationship between humans and AI.05/2024
TCS iON Career Edge - Young Professional
TCS iON
Gained expertise in: Communication Skills,Presentation Skills,Soft
Skills,Group Discussion Skills,IT Foundational Skills,Overview of
Artificial Intelligence.07/2024
Extracurricular Activities
Event Coordinator
Conducted Coding Contest BLITZ 'N FIX 2.4 as a part of Intercollegiate Techno-Cultural Fest.
Technical Team Member
As a technical team member associated with the placement cell, actively contributed to
facilitating placement activities.
Fine Arts Participation
Achieved first prize in the Margamkali competition at the college arts festival.
Attended a Seminar: Symposium on Transformative Trends in Digital Technologies
Participated in a seminar organized by the Department of Physics and the Advanced Learnerʼs
Mentoring Cell (ALMC) at St. Thomas College (Autonomous), Thrissur."""

# Tokenize the text into sentences
file_docs = sent_tokenize(document_text)

# Preprocess the text (remove stopwords and punctuation)
stop_words = set(stopwords.words('english') + list(string.punctuation))

def preprocess_text(text):
    tokens = word_tokenize(text)
    tokens = [w.lower() for w in tokens if w.isalpha() and w.lower() not in stop_words]
    return tokens

gen_docs = [preprocess_text(text) for text in file_docs]

# Create a Gensim dictionary and corpus
dictionary = gensim.corpora.Dictionary(gen_docs)
corpus = [dictionary.doc2bow(gen_doc) for gen_doc in gen_docs]

# Create TF-IDF model
tf_idf = gensim.models.TfidfModel(corpus)

# Create a directory for storing the index matrix (if it doesn't exist already)
if not os.path.exists('workdir'):
    os.makedirs('workdir')

# Create the similarity object
sims = gensim.similarities.Similarity('workdir/', tf_idf[corpus], num_features=len(dictionary))

def calculate_similarity(query_text):
    file2_docs = sent_tokenize(query_text)
    query_doc_sims = []
    for line in file2_docs:
        query_doc = preprocess_text(line)
        query_doc_bow = dictionary.doc2bow(query_doc)

        # Perform a similarity query against the corpus
        query_doc_tf_idf = tf_idf[query_doc_bow]
        sim = sims[query_doc_tf_idf]
        query_doc_sims.append(sim)
    
    # Calculate sum of similarities for all sentences
    sum_of_sims = np.sum(query_doc_sims, dtype=np.float32)

    # Calculate average similarity
    average_similarity = sum_of_sims / len(file_docs)  # Normalize the similarity score by number of documents
    percentage_of_similarity = round(float(average_similarity) * 100)
    percentage_of_similarity = min(percentage_of_similarity, 100)  # Ensure it doesn't exceed 100%

    return percentage_of_similarity



import chardet

def home(request):
    if request.method == 'POST' and request.FILES['file']:
        uploaded_file = request.FILES['file']
        
        # Read the file content as bytes
        file_bytes = uploaded_file.read()
        
        # Use chardet to detect the file encoding
        result = chardet.detect(file_bytes)
        file_encoding = result['encoding']
        
        # If encoding is None (couldn't detect), fallback to 'utf-8' or another encoding
        if file_encoding is None:
            file_encoding = 'utf-8'  # Default to UTF-8

        # Decode the file content using the detected encoding
        try:
            query_text = file_bytes.decode(file_encoding)
        except UnicodeDecodeError:
            # Fallback: try 'utf-8' or 'iso-8859-1' if the detected encoding fails
            query_text = file_bytes.decode('utf-8', errors='ignore')

        # Calculate similarity percentage
        similarity_percentage = calculate_similarity(query_text)

        # Return the result to the template
        return render(request, 'project test 1.html', {'similarity_percentage': similarity_percentage})

    else:
        form = FileUploadForm()
        return render(request, 'project test 1.html', {'form': form})
    


def afterlogin_view(request):
     return render(request, 'afterlogin.html')

def features(request):
     return render(request, 'features.html')






import os
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from PyPDF2 import PdfReader
import docx
import google.generativeai as genai
import nltk

# Ensure nltk's Punkt tokenizer is downloaded
nltk.download('punkt')

# Configure the generative AI API
genai.configure(api_key='AIzaSyCjjQY-_DWVGzOFInkl_Ghqt8JTaJ7xuc4')


def read_pdf(file_path):
    """Reads and extracts text from a PDF file."""
    with open(file_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        text = ''.join(page.extract_text() or "" for page in pdf_reader.pages)
    return text


def read_docx(file_path):
    """Reads and extracts text from a Word document."""
    doc = docx.Document(file_path)
    return '\n'.join(paragraph.text for paragraph in doc.paragraphs)


def process_resume(request):
    if request.method == 'POST' and request.FILES['resume']:
        # Save the uploaded file
        uploaded_file = request.FILES['resume']
        fs = FileSystemStorage()
        file_path = fs.save(uploaded_file.name, uploaded_file)

        # Determine file type and extract text
        resume_text = ''
        file_path = fs.path(file_path)
        if uploaded_file.name.endswith('.pdf'):
            resume_text = read_pdf(file_path)
        elif uploaded_file.name.endswith('.docx'):
            resume_text = read_docx(file_path)
        else:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                resume_text = file.read()

        # Use Google Generative AI for analysis
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        response = model.generate_content(f"""
            You are an experienced career counselor. Review the following resume content provided as plain text, 
            identify errors, and provide section wise actionable recommendations for improvement:

            Resume Section Content:
            \"\"\"{resume_text}\"\"\"  
        """)

        # Render the response
        context = {
            'recommendations': response.text
        }
        return render(request, 'result.html', context)

    return render(request, 'upload.html')



def upload_resume(request):
    return render(request, 'upload.html')





from django.shortcuts import render
from django.http import JsonResponse
from .models import UserResume
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import pandas as pd
from PyPDF2 import PdfReader
from docx import Document
import json
import os

DATA_FILE = "job_data.json"

# Predefined initial job roles and skills
initial_data = {
    "Data Scientist": "machine learning, python, data analysis, statistics, big data, predictive modeling, data visualization, SQL, R, AI frameworks, data wrangling, feature engineering, Hadoop, Spark, business acumen, communication skills, time-series analysis, cloud computing, database management",
    "Software Engineer": "programming, software development, java, python, debugging, software architecture, version control, problem-solving, algorithms, data structures, software testing, REST APIs, microservices, cloud platforms, full-stack development, design patterns, performance optimization, teamwork",
    "Project Manager": "project management, communication, leadership, planning, budgeting, scheduling, risk management, stakeholder management, Agile, Scrum, conflict resolution, resource allocation, change management, team collaboration, negotiation, project scope definition, time management, project tracking tools",
    "Web Developer": "html, css, javascript, web development, responsive design, web performance, React, Angular, frontend frameworks, REST APIs, Vue.js, accessibility standards, cross-browser compatibility, backend integration, Node.js, Bootstrap, GraphQL, web security principles, testing/debugging tools",
    "System Administrator": "networking, system management, troubleshooting, linux, server maintenance, scripting, security protocols, virtualization, cloud services, Windows Server, database administration, backup and recovery, IT automation, system monitoring, IT compliance, disaster recovery, DNS, DHCP",
    "UX Designer": "user experience, design thinking, prototyping, wireframing, user research, usability testing, interaction design, visual design, Figma, Adobe XD, accessibility design, UX writing, motion design, design systems, empathy mapping, persona creation, heuristic evaluation, storytelling, cross-functional collaboration",
    "Business Analyst": "data analysis, requirements gathering, problem solving, communication, stakeholder engagement, documentation, process improvement, SQL, visualization tools, business intelligence, financial analysis, Tableau, Power BI, data storytelling, gap analysis, SWOT analysis, system integration, cost-benefit analysis",
    "Cybersecurity Specialist": "cybersecurity, network security, risk assessment, cryptography, ethical hacking, incident response, firewalls, penetration testing, security audits, vulnerability assessment, security frameworks, SIEM tools, compliance standards, forensic analysis, identity management, zero-trust architecture, threat modeling",
    "Cloud Engineer": "cloud computing, aws, azure, cloud architecture, containerization, Kubernetes, cloud security, serverless computing, cost optimization, Terraform, OpenStack, GCP, hybrid cloud solutions, cloud migration, cloud monitoring tools, API integration, DevOps principles, multi-cloud strategies",
    "AI Engineer": "artificial intelligence, deep learning, machine learning, python, neural networks, TensorFlow, PyTorch, NLP, computer vision, AI ethics, reinforcement learning, GANs, transfer learning, edge AI, AI model deployment, MLOps, algorithm optimization, GPU computing, cloud AI services, explainable AI",
    "DevOps Engineer": "devops, ci/cd, automation, containerization, Docker, Kubernetes, cloud platforms, infrastructure as code, monitoring, scripting, Jenkins, Ansible, Terraform, configuration management, system reliability, cloud cost optimization, incident response, system scalability, version control systems, Agile methodologies",
    "Database Administrator": "database management, sql, nosql, data modeling, database security, performance tuning, backup and recovery, Oracle, MySQL, PostgreSQL, MongoDB, database replication, clustering, query optimization, ETL processes, database monitoring, database migration, disaster recovery, schema design, database auditing",
    "Digital Marketing Specialist": "seo, social media, content marketing, google analytics, PPC campaigns, email marketing, keyword research, brand strategy, data analysis, influencer marketing, conversion rate optimization, A/B testing, marketing automation, CRM systems, mobile marketing, copywriting, video marketing, affiliate marketing",
    "Product Manager": "product lifecycle management, roadmap planning, customer research, agile methodologies, UX/UI principles, stakeholder communication, competitive analysis, MVP development, feature prioritization, market research, cross-functional team coordination, data-driven decision-making, product analytics, customer journey mapping, pricing strategies, business strategy",
    "Electrical Engineer": "circuit design, power systems, plc programming, embedded systems, signal processing, renewable energy systems, MATLAB, PCB design, IoT devices, electrical safety, high-voltage systems, power electronics, SCADA systems, control systems, microcontrollers, energy efficiency, project management",
    "Civil Engineer": "construction management, structural analysis, autocad, surveying, project planning, cost estimation, geotechnical engineering, sustainability, building codes, BIM software, construction materials, CAD software, foundation design, hydraulic engineering, urban planning, environmental impact assessment",
    "Content Writer": "copywriting, content creation, seo writing, storytelling, grammar, editing, research, creative writing, content strategy, audience engagement, social media writing, technical writing, blogging, brand voice, proofreading, long-form content, content repurposing, CMS platforms, analytics-driven content",
    "Human Resources Specialist": "recruitment, employee relations, training, hr policies, conflict resolution, performance management, payroll systems, compliance, organizational development, talent acquisition, HRIS systems, benefits administration, employee engagement, diversity and inclusion, labor law knowledge, succession planning, conflict mediation",
    "Graphic Designer": "adobe photoshop, adobe illustrator, typography, branding, color theory, layout design, visual storytelling, print design, digital media, creativity, motion graphics, 3D design, Canva, marketing campaigns, UX/UI design, illustration, photo editing, packaging design, web design principles",
    "Teacher": "teaching, curriculum development, classroom management, communication, lesson planning, student assessment, subject expertise, online teaching tools, mentoring, collaborative learning, differentiated instruction, educational technology, behavior management, parent communication, extracurricular activity planning, lifelong learning strategies, cultural competency",

}

# Load job roles from file and merge with initial data
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as file:
        existing_data = json.load(file)
else:
    existing_data = {}

# Merge datasets (existing data takes priority over initial data)
job_data = {**initial_data, **existing_data}

# Save the merged data back to JSON file
with open(DATA_FILE, "w") as file:
    json.dump(job_data, file, indent=4)

# Convert job data to DataFrame
job_roles_df = pd.DataFrame(list(job_data.items()), columns=["Job Role", "Required Skills"])

# TF-IDF and Nearest Neighbors model setup
tfidf_vectorizer = TfidfVectorizer()
skills_matrix = tfidf_vectorizer.fit_transform(job_roles_df["Required Skills"])
nn_model = NearestNeighbors(n_neighbors=3, metric="cosine")
nn_model.fit(skills_matrix)

def parse_resume2(file):
    """Extract text from uploaded resume file."""
    try:
        if file.name.endswith('.pdf'):
            pdf_reader = PdfReader(file.file)
            return " ".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
        elif file.name.endswith('.docx'):
            doc = Document(file.file)
            return " ".join(para.text for para in doc.paragraphs if para.text)
    except Exception as e:
        print(f"Error parsing file: {e}")
    return None

def predict_job_roles(resume_text):
    """Predict top job roles for given resume text."""
    resume_vector = tfidf_vectorizer.transform([resume_text])
    distances, indices = nn_model.kneighbors(resume_vector)

    return [
        (job_roles_df.iloc[i]["Job Role"], round((1 - distances[0][j]) * 100, 2))
        for j, i in enumerate(indices[0])
    ]

# def upload_resume2(request):
#     """Handle resume upload and job role prediction."""
#     if request.method == 'POST' and 'resume' in request.FILES:
#         file = request.FILES['resume']

#         # Extract text from resume
#         resume_text = parse_resume2(file)

#         if not resume_text:
#             return JsonResponse({"error": "Failed to extract text or unsupported file format"}, status=400)

#         # Predict job roles
#         predictions = predict_job_roles(resume_text)

#         # Save to the database
#         UserResume.objects.create(
#             uploaded_file=file,
#             extracted_text=resume_text,
#             prediction=str(predictions)  # Store as string, adjust if needed
#         )

#         # Render results
#         return render(request, 'upload_resume.html', {"predictions": predictions})

#     return render(request, 'upload_resume.html', {"error": "No file uploaded"})



def reload_and_train_model():
    """Reloads job roles and retrains the TF-IDF and Nearest Neighbors model dynamically."""
    global job_roles_df, tfidf_vectorizer, skills_matrix, nn_model

    # Reload job roles from JSON
    with open(DATA_FILE, "r") as file:
        job_data = json.load(file)

    # Convert to DataFrame
    job_roles_df = pd.DataFrame(list(job_data.items()), columns=["Job Role", "Required Skills"])

    # Retrain TF-IDF and Nearest Neighbors model
    tfidf_vectorizer = TfidfVectorizer()
    skills_matrix = tfidf_vectorizer.fit_transform(job_roles_df["Required Skills"])
    nn_model = NearestNeighbors(n_neighbors=3, metric="cosine")
    nn_model.fit(skills_matrix)


def upload_resume2(request):
    """Handle resume upload and job role prediction."""
    if request.method == 'POST' and 'resume' in request.FILES:
        file = request.FILES['resume']

        # Extract text from resume
        resume_text = parse_resume2(file)

        if not resume_text:
            return JsonResponse({"error": "Failed to extract text or unsupported file format"}, status=400)

        # 🔥 Dynamically reload job roles and retrain the model
        reload_and_train_model()

        # Predict job roles
        predictions = predict_job_roles(resume_text)

        # Save to the database
        UserResume.objects.create(
            uploaded_file=file,
            extracted_text=resume_text,
            prediction=str(predictions)  # Store as string, adjust if needed
        )

        # Render results
        return render(request, 'upload_resume.html', {"predictions": predictions})

    return render(request, 'upload_resume.html', {"error": "No file uploaded"})




from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.http import JsonResponse
import os
import PyPDF2
import docx
import re

# Function to parse skills from PDF
def parse_pdf2(file_path):
    skills = []
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text = page.extract_text()
            skills += extract_skills_from_text(text)
    return skills

# Function to parse skills from DOCX
def parse_docx2(file_path):
    skills = []
    doc = docx.Document(file_path)
    for para in doc.paragraphs:
        skills += extract_skills_from_text(para.text)
    return skills

# Function to extract skills from text using regular expressions or NLP
def extract_skills_from_text(text):
    skill_keywords = ['tensorflow', 'keras', 'pytorch', 'machine learning', 'deep learning', 'flask', 'streamlit', 'react', 'django', 'node js', 'react js', 'php', 'laravel', 'magento', 'wordpress', 'javascript', 'angular js', 'c#', 'asp.net', 'flutter', 'kotlin', 'xml', 'swift', 'cocoa', 'adobe xd', 'figma', 'zeplin', 'balsamiq', 'photoshop', 'illustrator', 'user research', 'english', 'communication', 'writing', 'microsoft office']
    
    # Simple regex to match skills in the text (can be expanded for NLP-based parsing)
    skills = [skill for skill in skill_keywords if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE)]
    return skills

# Main function to parse the resume and return skills
def parse_resume3(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == '.pdf':
        return parse_pdf2(file_path)
    elif file_extension == '.docx':
        return parse_docx2(file_path)
    else:
        raise ValueError("Unsupported file format. Please upload a PDF or DOCX file.")

def recommend_resources(request):
    if request.method == 'POST' and 'resume' in request.FILES:
        uploaded_file = request.FILES['resume']
        fs = FileSystemStorage()
        file_path = fs.save(uploaded_file.name, uploaded_file)
        file_full_path = fs.path(file_path)

        try:
            # Parse the uploaded resume
            parsed_skills = parse_resume3(file_full_path)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            # Clean up the file after parsing
            if os.path.exists(file_full_path):
                os.remove(file_full_path)

        # Define skill keywords
        ds_keyword = ['tensorflow', 'keras', 'pytorch', 'machine learning', 'deep learning', 'flask', 'streamlit']
        web_keyword = ['react', 'django', 'node js', 'react js', 'php', 'laravel', 'magento', 'wordpress', 'javascript', 'angular js', 'c#', 'asp.net', 'flask']
        android_keyword = ['android', 'android development', 'flutter', 'kotlin', 'xml', 'kivy']
        ios_keyword = ['ios', 'ios development', 'swift', 'cocoa', 'cocoa touch', 'xcode']
        uiux_keyword = ['ux', 'adobe xd', 'figma', 'zeplin', 'balsamiq', 'ui', 'prototyping', 'wireframes', 'photoshop', 'illustrator']
        n_any = ['english', 'communication', 'writing', 'microsoft office', 'leadership', 'customer management', 'social media']

        reco_field = ''
        recommended_skills = []
        resources = {}

        # Match skills to fields
        for skill in parsed_skills:
            skill_lower = skill.lower()
            if skill_lower in ds_keyword:
                reco_field = 'Data Science'
                resources['Data Science Courses'] = [
                    ["Machine Learning Crash Course by Google [Free]", "https://developers.google.com/machine-learning/crash-course"],
                    ["Machine Learning A-Z by Udemy", "https://www.udemy.com/course/machinelearning/"],
                ]
                break
            elif skill_lower in web_keyword:
                reco_field = 'Web Development'
                resources['Web Development Courses'] = [
                    ["Django Crash course [Free]", "https://youtu.be/e1IyzVyrLSU"],
                    ["Python and Django Full Stack Web Developer Bootcamp", "https://www.udemy.com/course/python-and-django-full-stack-web-developer-bootcamp"],
                ]
                break
            elif skill_lower in android_keyword:
                reco_field = 'Android Development'
                resources['Android Development Courses'] = [
                    ["Android Development for Beginners [Free]", "https://youtu.be/fis26HvvDII"],
                    ["Android App Development Specialization", "https://www.coursera.org/specializations/android-app-development"],
                ]
                break
            elif skill_lower in ios_keyword:
                reco_field = 'IOS Development'
                resources['iOS Development Courses'] = [
                    ["IOS App Development by LinkedIn", "https://www.linkedin.com/learning/subscription/topics/ios"],
                    ["iOS & Swift - The Complete iOS App Development Bootcamp", "https://www.udemy.com/course/ios-13-app-development-bootcamp/"],
                ]
                break
            elif skill_lower in uiux_keyword:
                reco_field = 'UI-UX Development'
                resources['UI/UX Design Courses'] = [
                    ["Google UX Design Professional Certificate", "https://www.coursera.org/professional-certificates/google-ux-design"],
                    ["UI / UX Design Specialization", "https://www.coursera.org/specializations/ui-ux-design"],
                ]
                break
            elif skill_lower in n_any:
                reco_field = 'NA'
                resources['General Skills'] = ["No Recommendations"]
                break

        # Render recommendations
        return render(request, 'resources.html', {"resources": resources, "reco_field": reco_field})

    return render(request, 'upload3.html')



import os
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from PyPDF2 import PdfReader
import docx
import google.generativeai as genai
import nltk

# Ensure nltk's Punkt tokenizer is downloaded
nltk.download('punkt')

# Configure the generative AI API
genai.configure(api_key='AIzaSyCjjQY-_DWVGzOFInkl_Ghqt8JTaJ7xuc4')


def read_pdf2(file_path):
    """Reads and extracts text from a PDF file."""
    with open(file_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        text = ''.join(page.extract_text() or "" for page in pdf_reader.pages)
    return text


def read_docx2(file_path):
    """Reads and extracts text from a Word document."""
    doc = docx.Document(file_path)
    return '\n'.join(paragraph.text for paragraph in doc.paragraphs)


def process_resume2(request):
    if request.method == 'POST' and request.FILES['resume']:
        # Save the uploaded file
        uploaded_file = request.FILES['resume']
        fs = FileSystemStorage()
        file_path = fs.save(uploaded_file.name, uploaded_file)

        # Determine file type and extract text
        resume_text = ''
        file_path = fs.path(file_path)
        if uploaded_file.name.endswith('.pdf'):
            resume_text = read_pdf(file_path)
        elif uploaded_file.name.endswith('.docx'):
            resume_text = read_docx(file_path)
        else:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                resume_text = file.read()

        # Use Google Generative AI for analysis
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(f"""
            Create a structured interview plan based on the resume, including:
            Technical questions tailored to the candidate’s listed skills.
            Behavioral questions related to past experience.
            Soft skills and cultural fit questions.
            Resume Section Content:
            \"\"\"{resume_text}\"\"\"  
        """)

        # Render the response
        context = {
            'recommendations': response.text
        }
        return render(request, 'result2.html', context)

    return render(request, 'upload4.html')




# from django.shortcuts import render
# from django.db.models import Q
# from .models import UserResume
# from django.conf import settings

# def view_resumes_inline(request):
#     if request.method == 'GET':
#         job_title = request.GET.get('job_title', '').strip()
        
#         if not job_title:
#             return render(request, 'view_resumes.html', {"error": "Job title is required"})

#         # Fetch resumes matching the job title
#         resumes = UserResume.objects.filter(
#             Q(prediction__icontains=job_title)
#         )
        
#         if not resumes.exists():
#             return render(request, 'view_resumes.html', {"message": "No resumes found for the given job title", "job_title": job_title})
        
#         # Render resumes to the template, include file URL for display
#         resume_data = []
#         for resume in resumes:
#             file_url = resume.uploaded_file.url  # Get the URL of the uploaded file

#             resume_data.append({
#                 'id': resume.id,
#                 'prediction': resume.prediction,
#                 'file_url': file_url,
#                 'file_name': resume.uploaded_file.name,
#             })
        
#         return render(request, 'view_resumes.html', {"resumes": resume_data, "job_title": job_title})






# from django.shortcuts import render
# from django.db.models import Q
# from .models import UserResume

# def view_resumes_inline(request):
#     job_title = request.GET.get('job_title', '').strip()

#     if not job_title:
#         return render(request, 'view_resumes.html', {"error": "Job title is required"})

#     # Fetch resumes matching the job title
#     resumes = UserResume.objects.filter(
#         Q(prediction__icontains=job_title)
#     ).values('id', 'uploaded_file', 'prediction')

#     if not resumes.exists():
#         return render(request, 'view_resumes.html', {"message": "No resumes found for the given job title", "job_title": job_title})

#     # Render resumes to the template
#     return render(request, 'view_resumes.html', {"resumes": resumes, "job_title": job_title})




# from django.shortcuts import render
# from django.db.models import Q
# from .models import UserResume

# def view_resumes_inline(request):
#     job_title = request.GET.get('job_title', '').strip()
#     resumes = None

#     if job_title:
#         # Filter resumes based on the job title in the prediction field
#         resumes = UserResume.objects.filter(
#             Q(prediction__icontains=job_title)
#         )

#     context = {
#         "job_title": job_title,
#         "resumes": resumes,
#         "message": "No resumes found" if job_title and not resumes else ""
#     }
#     return render(request, 'view_resumes.html', context)






# def view_resumes_inline(request):
#     job_title = request.GET.get('job_title', '').strip()
    
#     if not job_title:
#         return render(request, 'resume_management.html', {"error": "Please enter a job title to search."})

#     resumes = UserResume.objects.filter(prediction__icontains=job_title)
    
#     if not resumes.exists():
#         return render(request, 'resume_management.html', {"message": "No resumes found for the entered job title.", "job_title": job_title})

#     return render(request, 'resume_management.html', {"resumes": resumes, "job_title": job_title})



# def upload_resume5(request):
#     if request.method == 'POST' and 'resume' in request.FILES:
#         file = request.FILES['resume']
#         file_url = upload_to_google_drive(file)  # Upload to Google Drive and get the link
#         predictions = predict_job_roles(file)   # Predict job roles from the resume content
        
#         UserResume.objects.create(
#             uploaded_file=file,
#             file_url=file_url,
#             prediction=predictions
#         )
#         return render(request, 'resume_management.html', {"message": "Resume uploaded successfully."})

#     return render(request, 'resume_management.html')



from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .models import Company

def company_signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        email = request.POST["email"]
        company_name = request.POST["company_name"]

        if User.objects.filter(username=username).exists():
            return render(request, "company_signup.html", {"error": "Username already exists"})

        user = User.objects.create_user(username=username, email=email, password=password)
        company = Company.objects.create(user=user, name=company_name, approval_status="pending")

        return render(request, "company_signup.html", {"message": "Signup successful! Waiting for admin approval."})

    return render(request, "company_signup.html")
def company_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user:
            try:
                company = Company.objects.get(user=user)
                if company.approval_status == "approved":
                    login(request, user)
                    return redirect("company_dashboard")  # Redirect to dashboard
                else:
                    return render(request, "company_login.html", {"error": "Your company is not yet approved."})
            except Company.DoesNotExist:
                return render(request, "company_login.html", {"error": "Company record not found."})
        else:
            return render(request, "company_login.html", {"error": "Invalid username or password."})

    return render(request, "company_login.html")
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import get_object_or_404

# @login_required
# def review_queue(request):
#     if not request.user.is_staff:
#         return redirect("dashboard")  # Redirect non-admins to dashboard

#     pending_companies = Company.objects.filter(approval_status="pending")

#     if request.method == "POST":
#         for company_id in request.POST.getlist("approve"):
#             company = Company.objects.get(id=company_id)
#             company.approval_status = "approved"
#             company.save()

#         for company_id in request.POST.getlist("reject"):
#             company = Company.objects.get(id=company_id)
#             company.approval_status = "rejected"
#             company.save()

#         return redirect("review_queue")

#     return render(request, "review_queue.html", {"companies": pending_companies})
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    company = Company.objects.get(user=request.user)
    if company.approval_status != "approved":
        return render(request, "approval_pending.html")
    return render(request, "dashboard.html")







from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Company

# Function to send email when a company is approved
# def send_approval_email(company):
#     send_mail(
#         "Company Approved",
#         f"Congratulations! Your company '{company.name}' has been approved. You can now log in to your account.",
#         "rosemariyaviji@gmail.com",  # Change this to your actual sender email
#         [company.user.email],
#         fail_silently=False,
#     )

# @login_required
# def review_queue(request):
#     if not request.user.is_staff:  # Ensure only admins can access this page
#         return redirect("dashboard")

#     pending_companies = Company.objects.filter(approval_status="pending")

#     if request.method == "POST":
#         for company_id in request.POST.getlist("approve"):
#             company = Company.objects.get(id=company_id)
#             company.approval_status = "approved"
#             company.save()
#             send_approval_email(company)  # Send approval email after approving

#         for company_id in request.POST.getlist("reject"):
#             company = Company.objects.get(id=company_id)
#             company.approval_status = "rejected"
#             company.save()

#         return redirect("review_queue")

#     return render(request, "review_queue.html", {"companies": pending_companies})



import logging
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Company
from .utils import send_approval_email  # Ensure this function is defined in utils.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Company
logger = logging.getLogger(__name__)


# Function to check if the user is an admin
def is_admin(user):
    return user.is_staff

# Admin review queue view (restricted to admins)
@login_required
@user_passes_test(is_admin, login_url="/admin/login/")  # Redirects non-admins to Django Admin Login


# Set up logging


# @login_required
# def review_queue(request):
#     if not request.user.is_staff:  # Ensure only admins can access this page
#         messages.error(request, "You do not have permission to access this page.")
#         return redirect("dashboard")

#     pending_companies = Company.objects.filter(approval_status="pending")

#     if request.method == "POST":
#         approve_ids = request.POST.getlist("approve")
#         reject_ids = request.POST.getlist("reject")

#         # Approve selected companies
#         approved_companies = Company.objects.filter(id__in=approve_ids, approval_status="pending")
#         approved_companies.update(approval_status="approved")

#         # Send approval emails
#         for company in approved_companies:
#             send_approval_email(company)
#             logger.info(f"Company Approved: {company.name} (ID: {company.id})")

#         # Reject selected companies
#         rejected_companies = Company.objects.filter(id__in=reject_ids, approval_status="pending")
#         rejected_companies.update(approval_status="rejected")

#         for company in rejected_companies:
#             logger.info(f"Company Rejected: {company.name} (ID: {company.id})")

#         messages.success(request, "Companies have been processed successfully.")
#         return redirect("review_queue")

#     return render(request, "review_queue.html", {"companies": pending_companies})





@login_required
@user_passes_test(is_admin)
def review_queue(request):
    pending_companies = Company.objects.filter(approval_status="pending")

    if request.method == "POST":
        # Loop through each company to get their approval or rejection status
        for company in pending_companies:
            approve = request.POST.get(f"company_{company.id}") == "approve"
            reject = request.POST.get(f"company_{company.id}") == "reject"

            if approve:
                company.approval_status = "approved"
                company.save()
                messages.success(request, f"{company.name} has been approved.")
            elif reject:
                company.approval_status = "rejected"
                company.save()
                messages.success(request, f"{company.name} has been rejected.")
        
        return redirect("review_queue")

    return render(request, "review_queue.html", {"companies": pending_companies})






from django.shortcuts import render, redirect
from django.contrib import messages
import json
import os

DATA_FILE = "job_data.json"

# Load existing job data or create a new file with initial data
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as file:
        data = json.load(file)
else:
    data = {}  # Empty dictionary if no file exists
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Function to save data
def save_data():
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Django View
from django.shortcuts import render, redirect
from django.contrib import messages
import json
import os

DATA_FILE = "job_data.json"

# Load existing job data or create a new file with initial data
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as file:
        data = json.load(file)
else:
    data = {}  # Empty dictionary if no file exists
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Function to save data
def save_data():
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Django View
from django.shortcuts import render, redirect
from django.contrib import messages
import json
import os

DATA_FILE = "job_data.json"

# Load existing job data or create a new file with initial data
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as file:
        data = json.load(file)
else:
    data = {}  # Empty dictionary if no file exists
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Function to save data
def save_data():
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Django View
def company_dashboard(request):
    if request.method == "POST":
        job_role = request.POST.get("job_role").strip().lower()  # Convert to lowercase for consistency
        new_skills = request.POST.get("skills").strip()

        if job_role and new_skills:
            new_skills_set = set(map(lambda skill: skill.strip().lower(), new_skills.split(",")))  # Convert to lowercase

            # Find the existing job role (case insensitive)
            existing_job_role = next((role for role in data if role.lower() == job_role), None)

            if existing_job_role:
                # Merge new skills with existing ones
                existing_skills = set(map(lambda skill: skill.strip().lower(), data[existing_job_role].split(",")))
                updated_skills = existing_skills | new_skills_set  # Union of both sets

                # Store updated skills in Title Case for better readability
                data[existing_job_role] = ", ".join(sorted(skill.title() for skill in updated_skills))
                messages.success(request, f"Updated skills for '{existing_job_role}'.")
            else:
                # Store new job role in Title Case
                data[job_role.title()] = ", ".join(sorted(skill.title() for skill in new_skills_set))
                messages.success(request, f"Added new job role '{job_role.title()}'.")

            save_data()  # Save updated data

        return redirect("company_dashboard")

    # Display existing job role skills when the page loads
    job_role = request.GET.get('job_role', '').strip().lower()
    existing_job_role = next((role for role in data if role.lower() == job_role), None)
    current_skills = data.get(existing_job_role, '') if existing_job_role else ''

    return render(request, "dashboard.html", {
        "data": data,
        "current_skills": current_skills,
        "job_role": existing_job_role if existing_job_role else job_role.title()
    })



from django.http import JsonResponse

def fetch_skills(request):
    job_role = request.GET.get("job_role", "").strip().lower()
    existing_job_role = next((role for role in data if role.lower() == job_role), None)

    skills = data.get(existing_job_role, "") if existing_job_role else ""

    return JsonResponse({"skills": skills})






# from django.shortcuts import render
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# import pandas as pd
# import json
# import os
# import hashlib
# from .models import ResumeEntry
# from .utils import parse_resume  # Ensure you have a resume parsing function
# from django.core.files.storage import default_storage
# from django.core.files.base import ContentFile



# # Configure logging
# logging.basicConfig(
#     filename="error.log",  # Logs will be saved in error.log
#     level=logging.ERROR,
#     format="%(asctime)s - %(levelname)s - %(message)s",
# )

# # Load Job Role Skills from JSON
# DATA_FILE = "job_data.json"

# if os.path.exists(DATA_FILE):
#     with open(DATA_FILE, "r") as file:
#         job_data = json.load(file)
# else:
#     job_data = {}

# # Synonym Dictionary
# synonyms = {
#     "react.js": "react",
#     "ml": "machine learning",
#     "nlp": "natural language processing",
#     "js": "javascript",
#     "tf": "tensorflow",
#     "sql": "structured query language",
#     "cv": "computer vision",
# }

# def preprocess_skills(text):
#     """Replace synonyms to unify skill terms before processing."""
#     text = text.lower()
#     for key, value in synonyms.items():
#         text = text.replace(key, value)
#     return text

# def calculate_file_hash(file):
#     """Calculates the SHA-256 hash of a given file."""
#     hasher = hashlib.sha256()
    
#     # Read the file in chunks to handle large files efficiently
#     for chunk in file.chunks():
#         hasher.update(chunk)
    
#     return hasher.hexdigest()  # Returns the hexadecimal hash string

# @csrf_exempt
# def upload_resume5(request):
#     """Handles resume uploads and prevents duplicate submissions."""
#     if request.method == "POST":
#         if "resume" not in request.FILES:
#             return JsonResponse({"error": "No file uploaded."}, status=400)

#         file = request.FILES["resume"]
#         file_hash = calculate_file_hash(file)

#         try:
#             # Check for duplicate
#             if ResumeEntry.objects.filter(resume_hash=file_hash).exists():
#                 return JsonResponse({"error": "Duplicate resume detected! You have already uploaded this file."}, status=400)

#             # Save the file
#             resume = ResumeEntry(uploaded_file=file, resume_hash=file_hash)
#             resume.save()
#             return JsonResponse({"message": "Resume uploaded successfully!"})
        
#         except Exception as e:
#             return JsonResponse({"error": f"Server error: {str(e)}"}, status=500)

#     return render(request, "upload_resume5.html")



# import hashlib
# import logging
# import traceback
# from django.shortcuts import render
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from .models import ResumeEntry
# from .utils import parse_resume
# from django.core.files.storage import default_storage
# from django.core.files.base import ContentFile

# # Configure logging
# logging.basicConfig(
#     filename="error.log",  # Logs will be saved in error.log
#     level=logging.ERROR,
#     format="%(asctime)s - %(levelname)s - %(message)s",
# )

# @csrf_exempt
# def upload_resume5(request):
#     """Handles resume uploads, prevents duplicates, and extracts skills."""
#     try:
#         if request.method == "POST" and request.FILES.get("resume"):
#             file = request.FILES["resume"]
            
#             # Read file content for hashing
#             file_content = file.read()
#             file_hash = hashlib.sha256(file_content).hexdigest()
            
#             # Check for duplicates
#             if ResumeEntry.objects.filter(resume_hash=file_hash).exists():
#                 return JsonResponse({"error": "Duplicate resume detected"}, status=400)

#             # Save file
#             file_name = default_storage.save(f"resumes/{file.name}", ContentFile(file_content))

#             # Extract text
#             extracted_text = parse_resume(file)

#             if not extracted_text:
#                 return JsonResponse({"error": "Invalid or unreadable file"}, status=400)

#             # Save to DB
#             ResumeEntry.objects.create(
#                 uploaded_file=file_name, resume_hash=file_hash, extracted_text=extracted_text
#             )

#             return JsonResponse({"message": "Resume uploaded successfully"})

#         return JsonResponse({"error": "No file uploaded or invalid request"}, status=400)

#     except Exception as e:
#         error_message = f"Error uploading file: {e}"
#         print(error_message)  # Ensure it prints
#         logging.error(error_message)  # Log error to file
#         traceback.print_exc()  # Print full error details
#         return JsonResponse({"error": "Error uploading file. Check logs for details."}, status=500)


# from django.shortcuts import render
# from django.http import JsonResponse
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# import pandas as pd
# from .models import ResumeEntry

# def search_resumes(request):
#     """Find resumes with at least one matching skill and sort by highest similarity score."""
#     job_role = request.GET.get("job_role", "").strip().lower()
    
#     if not job_role:
#         return JsonResponse({"error": "Job role is required"}, status=400)

#     required_skills = preprocess_skills(job_role)  # Assuming `preprocess_skills` function exists

#     # Fetch stored resumes
#     resumes = ResumeEntry.objects.values("id", "extracted_text", "uploaded_file")
#     resumes_df = pd.DataFrame(list(resumes))

#     if resumes_df.empty:
#         return JsonResponse({"resumes": []})

#     resumes_df["processed_skills"] = resumes_df["extracted_text"].apply(preprocess_skills)

#     # TF-IDF Vectorization
#     tfidf = TfidfVectorizer()
#     all_texts = [required_skills] + resumes_df["processed_skills"].tolist()
#     tfidf_matrix = tfidf.fit_transform(all_texts)

#     # Compute Cosine Similarity
#     similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
#     resumes_df["score"] = similarities

#     # Filter resumes with matching skills
#     matching_resumes = resumes_df[resumes_df["score"] > 0].sort_values(by="score", ascending=False)

#     # Include file URLs
#     matching_resumes["file_url"] = matching_resumes["uploaded_file"].apply(lambda file: f"/media/{file}" if file else "")

#     return JsonResponse({"resumes": matching_resumes[["id", "extracted_text", "score", "file_url"]].to_dict(orient="records")})
