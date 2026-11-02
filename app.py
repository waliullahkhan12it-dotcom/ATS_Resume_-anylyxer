import streamlit as st
import os
import json
import re
import io
from groq import Groq
from pypdf import PdfReader
from docx import Document

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="ResumeIQ | AI ATS Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #101827, #17243b, #101827);
    color: #f1f5f9;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1250px;
}

.hero {
    background: linear-gradient(120deg, #4338ca, #7c3aed, #0ea5e9);
    padding: 35px;
    border-radius: 20px;
    margin-bottom: 25px;
    box-shadow: 0 10px 35px rgba(0,0,0,0.25);
}

.hero h1 {
    color: white;
    font-size: 38px;
    font-weight: 800;
    margin-bottom: 8px;
}

.hero p {
    color: #e0e7ff;
    font-size: 16px;
}

.section-card {
    background: #1e293b;
    border: 1px solid #334155;
    padding: 22px;
    border-radius: 16px;
    margin-bottom: 18px;
}

.metric-card {
    background: linear-gradient(145deg, #1e293b, #263750);
    border: 1px solid #475569;
    border-radius: 16px;
    padding: 22px;
    text-align: center;
}

.metric-number {
    font-size: 34px;
    font-weight: 800;
    color: #38bdf8;
}

.metric-label {
    font-size: 14px;
    color: #cbd5e1;
}

.stButton > button {
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 700;
    min-height: 48px;
    width: 100%;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #4f46e5, #7c3aed);
    color: white;
    border: none;
}

h1, h2, h3 {
    color: #f8fafc;
}

label, p, li {
    color: #e2e8f0;
}

[data-testid="stFileUploader"] {
    background: #1e293b;
    padding: 18px;
    border-radius: 14px;
    border: 1px dashed #818cf8;
}

div[data-testid="stProgressBar"] > div > div {
    background-color: #38bdf8;
}

.small-note {
    color: #94a3b8;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown("""
<div class="hero">
    <h1>📄 ResumeIQ</h1>
    <p>AI-Powered Resume Analyzer | ATS Score | Smart Career Recommendations</p>
    <p>Make your resume stronger, smarter and more job-ready.</p>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# API KEY
# --------------------------------------------------

def get_api_key():
    try:
        key = st.secrets.get("GROQ_API_KEY", "")
        if key:
            return key
    except Exception:
        pass

    return os.getenv("GROQ_API_KEY", "")


# --------------------------------------------------
# RESUME TEXT EXTRACTION
# --------------------------------------------------

def extract_resume_text(uploaded_file):

    file_bytes = uploaded_file.getvalue()
    filename = uploaded_file.name.lower()

    if filename.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(file_bytes))

        if reader.is_encrypted:
            raise ValueError("Password-protected PDFs are not supported.")

        pages = []

        for page in reader.pages:
            pages.append(page.extract_text() or "")

        text = "\n".join(pages)

    elif filename.endswith(".docx"):
        document = Document(io.BytesIO(file_bytes))

        paragraphs = [
            paragraph.text for paragraph in document.paragraphs
        ]

        table_text = []

        for table in document.tables:
            for row in table.rows:
                table_text.append(
                    " | ".join(cell.text for cell in row.cells)
                )

        text = "\n".join(paragraphs + table_text)

    else:
        raise ValueError("Please upload a PDF or DOCX file.")

    text = re.sub(r'\n{3,}', '\n\n', text).strip()

    if len(text) < 100:
        raise ValueError(
            "Very little text was extracted. Your resume may be scanned "
            "or image-based. Please upload a text-based PDF or DOCX."
        )

    if len(text) > 30000:
        text = text[:30000]

    return text


# --------------------------------------------------
# AI RESUME ANALYSIS
# --------------------------------------------------

def analyze_resume(resume_text, job_description):

    api_key = get_api_key()

    if not api_key:
        raise ValueError(
            "Groq API key is missing. Add GROQ_API_KEY to Streamlit Secrets."
        )

    client = Groq(api_key=api_key)

    job_context = job_description.strip()

    if not job_context:
        job_context = (
            "No specific job description supplied. "
            "Evaluate the resume for general professional ATS readiness."
        )

    prompt = f"""
You are an expert Applicant Tracking System (ATS) resume evaluator
and professional career coach.

Analyze the resume against the supplied job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_context}

Return ONLY valid JSON. Do not use markdown or code fences.

Use exactly this JSON structure:

{{
  "ats_score": 75,
  "score_explanation": "Short explanation of the score",
  "summary": "Overall resume evaluation",
  "strengths": [
    "Strength 1",
    "Strength 2"
  ],
  "weaknesses": [
    "Weakness 1",
    "Weakness 2"
  ],
  "missing_keywords": [
    "Keyword 1",
    "Keyword 2"
  ],
  "skills_found": [
    "Skill 1",
    "Skill 2"
  ],
  "section_feedback": {{
    "Professional Summary": "Feedback",
    "Work Experience": "Feedback",
    "Education": "Feedback",
    "Skills": "Feedback",
    "Projects": "Feedback"
  }},
  "improvements": [
    "Actionable improvement 1",
    "Actionable improvement 2"
  ],
  "improved_summary": "Write a professional improved resume summary based ONLY on information supported by the original resume. Do not invent experience, qualifications or achievements.",
  "recommendation": "Final career recommendation"
}}

IMPORTANT RULES:

1. ATS score must be an integer between 0 and 100.
2. Evaluate keyword relevance, skills, formatting indicators,
   experience, education and readability.
3. If no job description is supplied, evaluate general ATS readiness.
4. Do not invent missing skills or qualifications.
5. Be specific and practical.
6. Never claim that this is an actual score from a particular ATS vendor.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": "You are a professional resume ATS analyzer. Return valid JSON only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        max_completion_tokens=3000
    )

    result = response.choices[0].message.content

    if not result:
        raise ValueError("The AI returned an empty response. Please try again.")

    # Extract JSON even if the model adds code fences
    match = re.search(r'\{.*\}', result, re.DOTALL)

    if not match:
        raise ValueError("AI response was not valid JSON. Please try again.")

    data = json.loads(match.group())

    score = data.get("ats_score")

    if isinstance(score, bool) or not isinstance(score, (int, float)):
        raise ValueError("The AI returned an invalid ATS score.")

    data["ats_score"] = max(0, min(100, int(score)))

    return data


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.markdown("## 🚀 ResumeIQ")

    st.markdown("---")

    st.markdown("### 📌 How it works")

    st.markdown("""
    1. Upload your resume.
    2. Add a job description.
    3. Click Analyze Resume.
    4. View your ATS score.
    5. Improve your resume.
    """)

    st.markdown("---")

    st.markdown("### 🛠 Technology")

    st.write("🐍 Python")
    st.write("🎨 Streamlit")
    st.write("🧠 Groq AI")
    st.write("📊 ATS Analysis")

    st.markdown("---")

    st.caption("ResumeIQ | AI Career Assistant")


# --------------------------------------------------
# MAIN INPUT SECTION
# --------------------------------------------------

st.markdown("## 📤 Upload Your Resume")

st.markdown("""
<div class="section-card">
    <h3>Let's analyze your resume!</h3>
    <p>Upload your resume in PDF or DOCX format.</p>
    <p class="small-note">Maximum file size: 5 MB</p>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choose your resume",
    type=["pdf", "docx"],
    help="Supported formats: PDF and DOCX"
)

st.markdown("### 🎯 Target Job Description")

job_description = st.text_area(
    "Paste the job description here (optional)",
    placeholder="Paste the job requirements, responsibilities and skills here...",
    height=160
)

st.caption(
    "Providing a job description allows a more relevant keyword "
    "and skills comparison."
)

analyze_button = st.button(
    "🚀 Analyze My Resume",
    use_container_width=True
)


# --------------------------------------------------
# ANALYSIS PROCESS
# --------------------------------------------------

if analyze_button:

    if uploaded_file is None:

        st.error("Please upload a resume first.")

    elif uploaded_file.size > 5 * 1024 * 1024:

        st.error("File is too large. Maximum allowed size is 5 MB.")

    else:

        try:

            with st.spinner("📄 Extracting resume text..."):
                resume_text = extract_resume_text(uploaded_file)

            with st.spinner(
                "🧠 Groq AI is analyzing your resume. Please wait..."
            ):
                analysis = analyze_resume(
                    resume_text,
                    job_description
                )

            st.session_state["analysis"] = analysis

            st.session_state["resume_name"] = uploaded_file.name

            st.success("Resume analysis completed successfully!")

        except Exception as error:

            st.error(f"Analysis failed: {error}")


# --------------------------------------------------
# RESULTS DASHBOARD
# --------------------------------------------------

if "analysis" in st.session_state:

    data = st.session_state["analysis"]

    st.markdown("---")

    st.markdown("## 📊 Resume Analysis Dashboard")

    st.caption(
        f"Analyzed file: {st.session_state['resume_name']}"
    )

    score = data["ats_score"]

    if score >= 80:
        score_label = "Excellent"
        score_color = "#22c55e"
    elif score >= 60:
        score_label = "Good"
        score_color = "#38bdf8"
    elif score >= 40:
        score_label = "Needs Improvement"
        score_color = "#f59e0b"
    else:
        score_label = "Weak"
        score_color = "#ef4444"

    # ATS SCORE

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{score}/100</div>
            <div class="metric-label">ATS Compatibility Score</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number" style="color:{score_color}">
                {score_label}
            </div>
            <div class="metric-label">Resume Assessment</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">
                {len(data.get("improvements", []))}
            </div>
            <div class="metric-label">Suggested Improvements</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 📈 ATS Score Visualization")

    st.progress(score / 100)

    st.markdown(
        f"**Score explanation:** {data.get('score_explanation', '')}"
    )

    # SUMMARY

    st.markdown("### 📝 Overall Resume Review")

    st.info(data.get("summary", "No summary available."))

    # STRENGTHS AND WEAKNESSES

    left, right = st.columns(2)

    with left:

        st.markdown("### ✅ Resume Strengths")

        for item in data.get("strengths", []):
            st.success(item)

    with right:

        st.markdown("### ⚠️ Resume Weaknesses")

        for item in data.get("weaknesses", []):
            st.warning(item)

    # SKILLS

    st.markdown("---")

    st.markdown("### 💡 Skills Identified")

    skills = data.get("skills_found", [])

    if skills:
        st.write(" | ".join([f"`{skill}`" for skill in skills]))
    else:
        st.write("No specific skills identified.")

    # KEYWORDS

    st.markdown("### 🔍 Missing Keywords")

    keywords = data.get("missing_keywords", [])

    if keywords:

        for keyword in keywords:
            st.markdown(f"- 🔴 {keyword}")

    else:

        st.success("No significant missing keywords identified.")

    # SECTION FEEDBACK

    st.markdown("---")

    st.markdown("### 📂 Section-by-Section Feedback")

    feedback = data.get("section_feedback", {})

    for section, comments in feedback.items():

        with st.expander(f"📌 {section}"):

            st.write(comments)

    # IMPROVEMENTS

    st.markdown("---")

    st.markdown("### 🚀 Recommended Improvements")

    for index, improvement in enumerate(
        data.get("improvements", []), start=1
    ):

        st.markdown(f"**{index}.** {improvement}")

    # IMPROVED SUMMARY

    st.markdown("---")

    st.markdown("### ✨ Improved Professional Summary")

    improved_summary = data.get("improved_summary", "")

    st.text_area(
        "Your suggested professional summary",
        value=improved_summary,
        height=150,
        key="improved_summary_box"
    )

    st.download_button(
        "⬇️ Download Improved Summary",
        data=improved_summary,
        file_name="improved_resume_summary.txt",
        mime="text/plain",
        use_container_width=True
    )

    # FINAL RECOMMENDATION

    st.markdown("---")

    st.markdown("### 🏆 AI Career Recommendation")

    st.success(
        data.get("recommendation", "Keep improving your resume.")
    )

    st.caption(
        "Disclaimer: This is an AI-generated estimate, not an official "
        "ATS vendor score or a guarantee of passing an employer's screening. "
        "Always verify suggestions before changing your resume."
    )

    # DOWNLOAD REPORT

    report = json.dumps(data, indent=4, ensure_ascii=False)

    st.download_button(
        "📥 Download Complete Analysis Report",
        data=report,
        file_name="resume_analysis_report.json",
        mime="application/json",
        use_container_width=True
    )

    if st.button("🔄 Analyze Another Resume"):

        del st.session_state["analysis"]

        if "resume_name" in st.session_state:
            del st.session_state["resume_name"]

        st.rerun()


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("---")

st.markdown(
    "<p style='text-align:center;color:#94a3b8;'>"
    "Made with ❤️ using Python, Streamlit and Groq AI | ResumeIQ"
    "</p>",
    unsafe_allow_html=True
)
