import streamlit as st
import pdfplumber
import docx2txt
import spacy
import re
import pandas as pd

nlp = spacy.load("en_core_web_sm")

def extract_pdf_text(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + " "
    return text

def extract_docx_text(path):
    return docx2txt.process(path)

def clean_text(t):
    return re.sub(r"\s+"," ",t.replace("\n"," ")).strip()

def extract_name(text):
    top = text[:150]
    words = top.split()
    name_words = []

    for w in words:
        if "@" in w or any(x.isdigit() for x in w):
            break
        clean = re.sub(r"[^A-Za-z]", "", w)
        if clean:
            name_words.append(clean)
        if len(name_words) == 3:
            break

    if 2 <= len(name_words) <= 4:
        return " ".join(name_words).title()

    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return ""

def extract_email(t):
    m = re.findall(r"[a-zA-Z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", t)
    return m[0] if m else ""

def extract_phone(t):
    m = re.findall(r"\+?\d[\d -]{7,15}", t)
    return m[0] if m else ""

SKILLS = [
    "python","java","c++","sql","nlp","html","css","react","javascript",
    "machine learning","deep learning","django","flask","data analysis"
]

def extract_skills(t):
    tl = t.lower()
    return ", ".join({s for s in SKILLS if s in tl})

def parse_resume(text):
    t = clean_text(text)
    return {
        "Name": extract_name(t),
        "Email": extract_email(t),
        "Phone": extract_phone(t),
        "Skills": extract_skills(t)
    }

# --------------- STREAMLIT UI ------------------

st.title("📄 Resume Parsing System")
st.write("Upload multiple resumes (PDF/DOCX) and extract candidate information easily.")

uploaded_files = st.file_uploader("Upload Resumes", type=["pdf","docx"], accept_multiple_files=True)

if uploaded_files:
    results = []

    for file in uploaded_files:
        with open(file.name, "wb") as f:
            f.write(file.getbuffer())

        if file.name.endswith(".pdf"):
            text = extract_pdf_text(file.name)
        elif file.name.endswith(".docx"):
            text = extract_docx_text(file.name)

        data = parse_resume(text)
        data["Filename"] = file.name
        results.append(data)

    df = pd.DataFrame(results)
    st.dataframe(df)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download CSV",
        data=csv,
        file_name="parsed_resumes.csv",
        mime="text/csv"
    )

# ----------------- COPYRIGHT FOOTER ----------------------

st.markdown("""
<hr>

<center>
<h4>© Made by <b>PRAKASH & MANISH MEENA</b></h4>
<p><b>MNIT Jaipur — NLP Lab Project</b></p>
<p>Prakash (2022UCP1448) &nbsp; | &nbsp; Manish Meena (2022UCP1459)</p>
</center>

<hr>
""", unsafe_allow_html=True)
