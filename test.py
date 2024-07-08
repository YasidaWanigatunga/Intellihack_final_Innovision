import openai
from dotenv import load_dotenv

# Load the API key from .env file
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Function to get a response from OpenAI GPT-4
def get_openai_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-004",  # Use the appropriate engine for GPT-4
        prompt=prompt,
        max_tokens=500,  # Adjust the max tokens as needed
        n=1,
        stop=None,
        temperature=0.7
    )
    return response.choices[0].text.strip()

def main():
    # Prompt for user input
    query = input("Enter your research topic: ")

    if not query:
        print("Query is required")
        return

    try:
        # Formulate the prompt for GPT-4
        prompt = f"Provide a list of some recent and relevant research papers on {query}. Include a brief description for each paper."

        # Get the response from GPT-4
        response = get_openai_response(prompt)
        print(f"Response:\n{response}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
