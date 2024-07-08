# pylint: disable=import-error
import os
import re
import warnings
from PIL import Image
from pdf2image import convert_from_path
import google.generativeai as genai
import openai
from dotenv import load_dotenv
warnings.filterwarnings("ignore")

# Load the API key from .env file
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
poppler_path = os.getenv('poppler_path')
openai.api_key = os.getenv('OPENAI_API_KEY')

# Configure the genai with the Google API key
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-pro-vision')
#python referencing.py


def get_metadata(paper_path, model):
    
    # Convert PDF to images
    images = convert_from_path(paper_path, 600, poppler_path= poppler_path)

    # Save the first page as an image
    image_path = 'page0.jpg'
    images[0].save(image_path, 'JPEG')

    # Load the saved image
    img = Image.open(image_path)

    # Define the prompt for the model
    prompt = '''
    Please find the answers for the following questions from the image:
    title_query = "What is the title of this paper?"
    authors_query = "Who are the authors of this paper? Use full names."
    year_query = "Could you please tell me when this paper was published?"
    journal_query = "Which journal was this paper published in?"
    volume_query = "What is the volume number?"
    issue_query = "What is the issue number?"
    pages_query = "What are the page numbers?"
    doi_query = "What is the DOI number?"
    '''

    # Generate content using the model (you should replace this with your actual model call)
    response = model.generate_content([prompt, img])

    # Extract and return the generated text
    return response.text

    # Querying the vector index to extract metadata
    def extract_metadata(query):
        results = paper_vector_index.invoke(query)
        return results

    title_query = "What is the title of this paper?"
    authors_query = "Who are the authors of this paper?, Use full names"
    year_query = "When was this paper published?"
    journal_query = "What is the name of the journal?"
    volume_query = "What is the volume number?"
    issue_query = "What is the issue number?"
    pages_query = "What are the page numbers?"

    metadata = {
        "title": extract_metadata(title_query),
        "authors": extract_metadata(authors_query),
        "year": extract_metadata(year_query),
        "journal": extract_metadata(journal_query),
        "volume": extract_metadata(volume_query),
        "issue": extract_metadata(issue_query),
        "pages": extract_metadata(pages_query)
    }
    return metadata

def get_reference(style, metadata, custom='custom'):
    
    # Remove 'Metadata:' if it exists
    metadata = re.sub(r'Metadata:\s*', '', metadata)
    
    # parse metadata string into a dictionary
    metadata_dict = {}
    lines = metadata.strip().split('\n')
    for line in lines:
        key_value = re.split(r':\s*', line, maxsplit=1)
        if len(key_value) == 2:
            metadata_dict[key_value[0].strip()] = key_value[1].strip()
    
    if style == "APA":
        # Define the prompt for the model
        prompt = '''You are an expert in APA citations. Please write a bibliography for metadata using the following template:
        If DOI or URL is not given:
        Author, A. A., & Author, B. B. (Year of publication). Title of article in sentence case:
        Capitalize the first letter of the subtitle. Title of the Journal in Mixed Case and
        speacially write in italics, volume number inspeacially write in italics (issue number), pp. xx-xx.

        If it is given:
        Author, A. A., & Author, B. B. (Year of publication). Title of article in sentence case:
        Capitalize the first letter of the subtitle. Title of the Journal in Mixed Case and
        speacially write in italics, volume number speacially write in italics (issue number), pp. xx-xx. DOI or URL'''

    elif style == "IEEE":
        # Define the prompt for the model
        prompt = '''
        You are an expert in IEEE citations. Please write a bibliography using the following template. 
        Note that the example below should be replaced with specific metadata: 
        example:
        J. Carlson, D. Menicucci, P. Vorobieff, A. Mammoli, and H. He, "Infrared imaging method for flyby assessment 
        of solar thermal panel operation in field settings," Appl. Therm. Eng., vol. 70, no. 1, pp. 163-171, Sept. 2014. 
        Accessed Mar. 19, 2018. doi:10.1016/j.applthermaleng.2014.05.008. [Online]. 
        Available: https://www.sciencedirect.com/science/article/pii/S1359431114003561
        '''
    elif style == "HARVARD":
        prompt = '''
        You are an expert in HARVARD citations. Please write a bibliography using the following template. 
        Use below template.
        If DOI or URL is given: 
        Write Journal name in Italics
        A DOI specially should be written with the prefix https://doi.org/ followed by the DOI number
        Never put a full stop after a DOI or URL as it may be assumed that it is part of the
        DOI or URL and prevent it from working.
        • Enclose the title of the article in single quotation marks.
        • Capitalise the first letter of each of the main words of the journal title, but not the
        linking words such as "and", "for", "of" or "the"
        
        ex: Dobson, H. (2006) 'Mister Sparkle meets the 'Yakuza': depictions of Japan in The Simpsons', Journal of Popular Culture, 39(1), 
        pp. 44–68. doi:https://doi.org/10.1111/j.1540-5931.2006.00203.x
        '''

    else :
        prompt = custom

    # Generate content using the model
    response = response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": metadata}
        ],
        max_tokens=500
        )

    # Extract and return the generated text
    return response['choices'][0]['message']['content'].strip()

