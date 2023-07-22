from PyPDF2 import PdfReader
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, "rb") as f:
        reader = PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text



def categorize_resume(text):
    doc = nlp(text)
    categorized_data = {
        "education": [],
        "skills": [],
        "experience": []
    }

    # Extracting education details
    for sent in doc.sents:
        if any(word in sent.text.lower() for word in ['university', 'bachelor', 'master', 'diploma', 'degree']):
            categorized_data["education"].append(sent.text)

    # Extracting skills
    if "skills:" in text.lower():
        skills_section = text.lower().split("skills:")[1].split("\n")[0]
        skills = [skill.strip() for skill in skills_section.split(",")]
        categorized_data["skills"].extend(skills)

    # Extracting experiences (this remains unchanged)
    for ent in doc.ents:
        if ent.label_ == "ORG":
            if ent.root.head.text in ['at', 'of']:
                categorized_data["experience"].append(ent.text)

    return categorized_data



if __name__ == "__main__":
    # readResume("/Users/mac/Eti/CompetentPro/Competent_Profiles/src/components/pdf/a.pdf")
    
    pdf_path = "/Users/mac/Eti/CompetentPro/Competent_Profiles/src/components/pdf/a.pdf"
    resume_text = extract_text_from_pdf(pdf_path)

    categorized_data = categorize_resume(resume_text)
    for category, items in categorized_data.items():
        print(f"{category}:")
        for item in items:
            print(f"  - {item}")
        print("\n")
