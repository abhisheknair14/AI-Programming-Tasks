import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")


# Extract website content
def extract_website_content(url):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=20
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove unnecessary elements
    for element in soup([
        "script",
        "style",
        "nav",
        "footer",
        "header",
        "aside"
    ]):
        element.decompose()

    # Extract title
    title = soup.title.string.strip() if soup.title and soup.title.string else "Website"

    # Extract readable text
    content = soup.get_text(separator=" ", strip=True)

    return title, content


# Generate AI summary
def generate_summary(title, content):

    client = Groq(api_key=API_KEY)

    prompt = f"""
    Summarize the following website content.

    Website Title: {title}

    Instructions:
    1. Provide a short introduction.
    2. Identify the main points.
    3. Highlight important information.
    4. Use simple and understandable language.
    5. Avoid unnecessary repetition.

    Website Content:
    {content[:12000]}
    """

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content


# Main application
def main():

    print("\n====================================")
    print("       AI WEBSITE SUMMARIZER")
    print("====================================\n")

    if not API_KEY:
        print("Groq API key is not configured.")
        print("Add your API key to the .env file first.")
        return

    while True:

        url = input("\nEnter website URL (or type exit): ").strip()

        if url.lower() == "exit":
            print("\nThank you for using AI Website Summarizer!")
            break

        if not url.startswith(("http://", "https://")):
            print("Please enter a valid URL beginning with http:// or https://")
            continue

        try:

            print("\nExtracting website content...")

            title, content = extract_website_content(url)

            if not content:
                print("No readable content found.")
                continue

            print("Website:", title)
            print("Content extracted successfully!")

            print("\nGenerating AI summary...")

            summary = generate_summary(title, content)

            print("\n========== WEBSITE SUMMARY ==========\n")
            print(summary)
            print("\n=====================================\n")

        except requests.exceptions.RequestException as error:
            print("\nWebsite loading error:", error)

        except Exception as error:
            print("\nAn error occurred:", error)


if __name__ == "__main__":
    main()