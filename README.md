
# 📄 ResumeIQ – AI Resume ATS Analyzer

ResumeIQ is an AI-powered resume analysis application built using
Python, Streamlit and Groq AI.

It helps users evaluate their resumes, identify weaknesses,
discover missing keywords and improve their professional summaries.

## 🚀 Features

- Upload resumes in PDF and DOCX formats.
- AI-powered ATS compatibility scoring (0–100).
- Resume strengths and weaknesses analysis.
- Missing keyword identification.
- Skills identification.
- Section-by-section resume feedback.
- Professional improvement recommendations.
- AI-generated improved professional summary.
- Downloadable analysis report.
- Downloadable improved summary.
- Modern Streamlit dashboard.

## 🛠 Technologies Used

- Python
- Streamlit
- Groq API
- Groq GPT-OSS 120B
- PyPDF
- python-docx

## 📁 Project Structure

```text
ai-resume-ats-analyzer/
│
├── app.py
├── requirements.txt
└── README.md
```

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/ai-resume-ats-analyzer.git
```

Move into the project folder:

```bash
cd ai-resume-ats-analyzer
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## 🔑 API Configuration

Get an API key from:

https://console.groq.com/keys

For local development, create:

`.streamlit/secrets.toml`

Add:

```toml
GROQ_API_KEY = "your_groq_api_key"
```

Never upload your API key or secrets.toml to GitHub.

For Streamlit Community Cloud, configure the key
through the application's Secrets settings.

## ▶️ Run the Application

```bash
streamlit run app.py
```

## 📊 How It Works

1. User uploads a resume.
2. The application extracts the resume text.
3. The user optionally supplies a job description.
4. Groq AI analyzes the resume.
5. An ATS compatibility score is generated.
6. The application displays strengths, weaknesses,
   missing keywords and improvements.
7. The user can download the analysis report.

## ⚠️ Disclaimer

The ATS score is an AI-generated estimate and is not an
official score from any particular applicant tracking system.
Actual screening results depend on the employer's software
and recruitment criteria.

## 👨‍💻 Author

Developed as an AI-powered resume analysis project.
