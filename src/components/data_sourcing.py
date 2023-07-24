import spacy
import pdfplumber

nlp = spacy.load("en_core_web_sm")


def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text


def categorize_resume(text):
    doc = nlp(text)
    categorized_data = {
        "education": "",
        "skills": "",
        "experience": ""
    }

    lines = text.split('\n')

    # Extracting experiences
    experience_index = lines.index("Experience")
    for line in lines[experience_index+1:]:
        if line in ["EDUCATION", "SKILLS & TOOLS", "COMPETENCIES"]:
            break
        categorized_data["experience"] += line + "\n"

    # Extracting education
    education_index = lines.index("Education")
    for line in lines[education_index+1:]:
        if line in ["SKILLS & TOOLS", "COMPETENCIES", "PROFESSIONAL EXPERIENCE"]:
            break
        categorized_data["education"] += line + "\n"

    # Extracting skills
    if "SKILLS & TOOLS" in lines:
        skills_index = lines.index("SKILLS & TOOLS")
        for line in lines[skills_index+1:]:
            if line in ["EDUCATION", "COMPETENCIES", "PROFESSIONAL EXPERIENCE"]:
                break
            categorized_data["skills"] += line + "\n"

    return categorized_data


if __name__ == "__main__":

    pdf_path = "src/components/pdf/b.pdf"
    resume_text = extract_text_from_pdf(pdf_path)

    categorized_data = categorize_resume(resume_text)
    for category, items in categorized_data.items():
        print(category, items)
