import openai
import arxiv
from scholarly import scholarly
from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def fetch_arxiv_papers(topic, max_results=5):
    search = arxiv.Search(
        query=topic,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    papers = []
    for result in arxiv.Client().results(search):
        papers.append({
            'title': result.title,
            'authors': [author.name for author in result.authors],
            'summary': result.summary,
            'url': result.pdf_url,
            'published': result.published.strftime('%Y-%m-%d')
        })
    return papers

def fetch_scholar_papers(topic, max_results=5):
    search_query = scholarly.search_pubs(topic)
    papers = []
    for i, result in enumerate(search_query):
        if i >= max_results:
            break
        papers.append({
            'title': result['bib']['title'],
            'authors': result['bib'].get('author', 'No author available'),
            'summary': result['bib'].get('abstract', 'No abstract available'),
            'url': result.get('pub_url', 'No URL available'),
            'published': result['bib'].get('pub_year', 'No publication year available')
        })
    return papers

def get_gpt4_response(prompt):
    response = openai.ChatCompletion.create(
        # model="gpt-3.5-turbo",
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a highly accurate and detailed assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.5,
        top_p=1,
        n=1,
        stop=None
    )
    return response.choices[0].message['content'].strip()

def generate_context_from_papers(papers):
    context = ""
    for paper in papers:
        context += f"Title: {paper['title']}\nPublished: {paper['published']}\nURL: {paper['url']}\nSummary: {paper['summary']}\n\n"
    return context

@app.route('/get_research_answer', methods=['POST'])
def get_research_answer():
    data = request.json
    parameters = data.get('parameters', [])
    question = data.get('question', '')

    if len(parameters) < 1:
        return jsonify({"error": "Please provide at least one parameter."}), 400

    # Fetch papers based on the first parameter for simplicity
    topic = parameters[0]
    arxiv_papers = fetch_arxiv_papers(topic)
    scholar_papers = fetch_scholar_papers(topic)
    recent_papers = arxiv_papers + scholar_papers

    if not recent_papers:
        return jsonify({"error": "No papers found for the given topic."}), 404

    context = generate_context_from_papers(recent_papers)
    combined_prompt = f"Using the following research parameters: {', '.join(parameters)}, provide a highly accurate and detailed answer to the question: {question}"
    answer = get_gpt4_response(combined_prompt)

    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(debug=True)
