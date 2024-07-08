import os
import openai
import fitz  # PyMuPDF
from dotenv import load_dotenv

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


def compare_sections(sections_list):
    comparison_results = {}
    for section_name in sections_list[0].keys():
        comparison_prompt = (
                f"Compare the following {section_name} sections:\n\n" + "\n\n".join(
            [f"{section_name} {i + 1}:\n{sections[section_name]}" for i, sections in enumerate(sections_list)]
        ) + f"\n\nHighlight the similarities, differences, technologies used, and important points in the {section_name} sections."
        )

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": comparison_prompt}
            ],
            max_tokens=150,
            temperature=0.7,
        )

        comparison_results[section_name] = response.choices[0].message['content'].strip()
    return comparison_results


def main():
    # Get user input for up to 5 PDF files
    num_papers = int(input("Enter the number of research papers to compare (up to 5): "))
    if num_papers < 2 or num_papers > 5:
        print("Please enter a number between 2 and 5.")
        return

    pdf_paths = []
    for i in range(num_papers):
        pdf_path = input(f"Enter the path to research paper {i + 1} (PDF): ")
        if os.path.isfile(pdf_path):
            pdf_paths.append(pdf_path)
        else:
            print(f"File {pdf_path} not found.")
            return

    # Extract text from each PDF and truncate if necessary
    papers = [truncate_text(extract_text_from_pdf(pdf_path)) for pdf_path in pdf_paths]

    # Get sections and summarize each paper
    sections_list = [get_sections(paper) for paper in papers]

    # Compare the summaries of each section
    comparison_results = compare_sections(sections_list)
    for section, result in comparison_results.items():
        print(f"\nComparison Result for {section}:\n", result)


if __name__ == "__main__":
    main()
