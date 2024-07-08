import openai
import arxiv
from scholarly import scholarly
from multiprocessing import Pool, cpu_count
from dotenv import load_dotenv
import pandas as pd
from langchain.llms import OpenAI
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Set up the OpenAI API client
openai.api_key = os.getenv('OPENAI_API_KEY')
if openai.api_key is None:
    logger.error("OpenAI API key is not set. Please check your .env file.")
else:
    logger.info("OpenAI API key loaded successfully.")


def fetch_scholar_papers(topic, max_results=10):
    try:
        search_query = scholarly.search_pubs(topic)
        papers = []
        for i, result in enumerate(search_query):
            if i >= max_results:
                break
            papers.append({
                'title': result['bib'].get('title', 'No title available'),
                'authors': result['bib'].get('author', 'No author available'),
                'abstract': result['bib'].get('abstract', 'No abstract available'),
                'url': result.get('pub_url', 'No URL available'),
                'published': result['bib'].get('pub_year', 'No publication year available')
            })
        return papers
    except Exception as e:
        logger.error(f"Error fetching Google Scholar papers: {e}")
        return []


def fetch_arxiv_papers(topic, max_results=5):
    try:
        search = arxiv.Search(
            query=topic,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        papers = []
        for result in search.results():
            papers.append({
                'title': result.title,
                'authors': [author.name for author in result.authors],
                'abstract': result.summary,
                'url': result.pdf_url,
                'published': result.published.strftime('%Y-%m-%d')
            })
        return papers
    except Exception as e:
        logger.error(f"Error fetching arXiv papers: {e}")
        return []


def get_gpt4_summary(abstract):
    try:
        prompt = f"Extract the main points from the following abstract:\n\n{abstract}\n\nMain points:"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a highly accurate and detailed assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.5,
            top_p=1,
            n=1,
            stop=None
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        logger.error(f"Error generating GPT-4 summary: {e}")
        return "Error generating summary."


def summarize_paper(paper):
    abstract = paper['abstract']
    summary = get_gpt4_summary(abstract)
    return {
        'title': paper['title'],
        'summary': summary,
        'url': paper['url']
    }


def save_summaries_to_excel(summaries, filename="research_summaries.xlsx"):
    df = pd.DataFrame(summaries)
    df.to_excel(filename, index=False)
    logger.info(f"Summaries saved to {filename}")


def load_summaries_from_excel(filename="research_summaries.xlsx"):
    df = pd.read_excel(filename)
    return df.to_dict(orient='records')


def get_gpt4_answer(parameters, question, summaries):
    try:
        combined_prompt = f"Using the following research parameters: {', '.join(parameters)}, answer the question: {question}\n\nSummaries of research papers:\n"
        for summary in summaries:
            combined_prompt += f"Title: {summary['title']}\nSummary: {summary['summary']}\nURL: {summary['url']}\n\n"
        combined_prompt += "Based on the above summaries, here is the answer to the question:"

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a highly accurate and detailed assistant."},
                {"role": "user", "content": combined_prompt}
            ],
            max_tokens=300,
            temperature=0.5,
            top_p=1,
            n=1,
            stop=None
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        logger.error(f"Error generating GPT-4 answer: {e}")
        return "Error generating answer."


def main():
    parameters = []
    print("Enter research parameters (type 'done' when finished):")
    while True:
        parameter = input("Enter a research parameter: ")
        if parameter.lower() == 'done':
            break
        parameters.append(parameter)

    if len(parameters) < 1:
        print("Please provide at least one parameter.")
        return

    question = input("Enter the research question: ")

    topic = parameters[0]  # For simplicity, use the first parameter for search
    scholar_papers = fetch_scholar_papers(topic)
    arxiv_papers = fetch_arxiv_papers(topic)

    if not scholar_papers and not arxiv_papers:
        print("No papers found for the given topic.")
        return

    all_papers = scholar_papers + arxiv_papers

    # Use multiprocessing to summarize papers in parallel
    with Pool(cpu_count()) as p:
        summaries = p.map(summarize_paper, all_papers)

    print("Summaries of research papers:")
    for summary in summaries:
        print(f"Title: {summary['title']}\nSummary: {summary['summary']}\nURL: {summary['url']}\n")

    # Save summaries to Excel
    save_summaries_to_excel(summaries)

    # Get the answer to the research question based on the summaries
    answer = get_gpt4_answer(parameters, question, summaries)
    print("\nAnswer to the research question:")
    print(answer)


class ResearchChatBot:
    def __init__(self, summaries):
        self.summaries = summaries
        self.llm = OpenAI(model="gpt-3.5-turbo")

    def generate_answer(self, question):
        combined_prompt = "Based on the following research summaries, answer the question:\n\n"
        for summary in self.summaries:
            combined_prompt += f"Title: {summary['title']}\nSummary: {summary['summary']}\nURL: {summary['url']}\n\n"
        combined_prompt += f"Question: {question}\nAnswer:"

        response = self.llm(combined_prompt)
        return response


def main_chatbot():
    summaries = load_summaries_from_excel()
    if not summaries:
        print("No summaries found. Please run the main function first to fetch and summarize papers.")
        return

    chatbot = ResearchChatBot(summaries)

    while True:
        question = input("Ask a question about the research papers (or type 'exit' to quit): ")
        if question.lower() == 'exit':
            break
        answer = chatbot.generate_answer(question)
        print("\nAnswer:")
        print(answer)


if __name__ == '__main__':
    main()
    main_chatbot()
