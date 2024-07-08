import os
import openai
import fitz  # PyMuPDF
from dotenv import load_dotenv
import pyttsx3

# Load the API key from .env file
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

MAX_TOKENS = 3000  # Adjust to ensure the text fits within the model's context limits


def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text


def truncate_text(text, max_length=MAX_TOKENS):
    return text[:max_length]


def summarize_section(section_text, section_name):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user",
             "content": f"Summarize the following {section_name} section of a research paper:\n\n{section_text}"}
        ],
        max_tokens=150,
        temperature=0.7,
    )
    return response.choices[0].message['content'].strip()


def get_sections(paper_text):
    sections = {}
    sections['abstract'] = summarize_section(paper_text, "abstract")
    sections['introduction'] = summarize_section(paper_text, "introduction")
    sections['methodology'] = summarize_section(paper_text, "methodology")
    sections['results'] = summarize_section(paper_text, "results")
    sections['conclusion'] = summarize_section(paper_text, "conclusion")
    return sections


def narrate_summary(summary_text):
    tts_engine = pyttsx3.init()
    tts_engine.setProperty('rate', 150)  # Speed of speech
    tts_engine.setProperty('volume', 1)  # Volume (0.0 to 1.0)

    tts_engine.say(summary_text)
    tts_engine.runAndWait()


def main():
    # Get user input for a PDF file
    pdf_path = input("Enter the path to the research paper (PDF): ")
    if not os.path.isfile(pdf_path):
        print(f"File {pdf_path} not found.")
        return

    # Extract text from the PDF and truncate if necessary
    paper_text = truncate_text(extract_text_from_pdf(pdf_path))

    # Get sections and summarize the paper
    sections = get_sections(paper_text)

    # Combine summaries for narration
    combined_summary = (
        f"Abstract:\n{sections['abstract']}\n\n"
        f"Introduction:\n{sections['introduction']}\n\n"
        f"Methodology:\n{sections['methodology']}\n\n"
        f"Results:\n{sections['results']}\n\n"
        f"Conclusion:\n{sections['conclusion']}\n\n"
    )

    print("Summary for Narration:\n", combined_summary)

    # Narrate the summary
    narrate_summary(combined_summary)


if __name__ == "__main__":
    main()
