import os
import numpy as np
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

# Initialize embedding model
print("\nLoading AI embedding model...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Read PDF
def read_pdf(file_path):
    reader = PdfReader(file_path)
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text()

        if text and text.strip():
            pages.append({
                "text": text,
                "page": page_number
            })

    return pages


# Split text into smaller chunks
def create_chunks(pages, chunk_size=500, overlap=100):
    chunks = []
    chunk_pages = []

    for page in pages:
        text = page["text"]

        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)
                chunk_pages.append(page["page"])

            start += chunk_size - overlap

    return chunks, chunk_pages


# Create embeddings
def create_embeddings(chunks):
    embeddings = embedding_model.encode(
        chunks,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    return embeddings


# Retrieve relevant chunks
def retrieve_context(question, chunks, embeddings, chunk_pages):
    question_embedding = embedding_model.encode(
        [question],
        convert_to_numpy=True,
        normalize_embeddings=True
    )[0]

    similarities = embeddings @ question_embedding

    top_indices = np.argsort(similarities)[::-1][:3]

    results = []

    for index in top_indices:
        results.append(
            f"[Page {chunk_pages[index]}]\n{chunks[index]}"
        )

    return "\n\n".join(results)


# Generate answer using Groq
def generate_answer(question, context):
    if not API_KEY:
        return None

    client = Groq(api_key=API_KEY)

    prompt = f"""
    Answer the question using only the information provided below.

    If the answer is not available in the document,
    clearly say that you could not find it.

    Document Context:
    {context}

    Question:
    {question}
    """

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content


# Main application
def main():

    print("\n===================================")
    print("       AI PDF RAG CHATBOT")
    print("===================================\n")

    file_path = input("Enter the PDF file path: ").strip().strip('"')

    if not os.path.isfile(file_path):
        print("Error: PDF file not found.")
        return

    if not file_path.lower().endswith(".pdf"):
        print("Error: Please provide a PDF file.")
        return

    print("\nReading PDF...")

    try:
        pages = read_pdf(file_path)

        if not pages:
            print("No readable text found in this PDF.")
            return

        print(f"Successfully extracted text from {len(pages)} pages.")

        print("\nSplitting document into chunks...")

        chunks, chunk_pages = create_chunks(pages)

        if not chunks:
            print("No text chunks were created.")
            return

        print(f"Created {len(chunks)} text chunks.")

        print("\nCreating embeddings...")

        embeddings = create_embeddings(chunks)

        print("Document processed successfully!")

        if not API_KEY:
            print("\nGroq API key is not configured yet.")
            print("You can test document retrieval now.")
        else:
            print("\nAI chatbot is ready!")

        print("\nType 'exit' to stop chatting.\n")

        while True:

            question = input("You: ").strip()

            if question.lower() == "exit":
                print("\nThank you for using the chatbot!")
                break

            if not question:
                continue

            context = retrieve_context(
                question,
                chunks,
                embeddings,
                chunk_pages
            )

            if not API_KEY:
                print("\nRetrieved document information:\n")
                print(context)
                print("\nAdd your Groq API key to enable AI-generated answers.\n")
                continue

            print("\nGenerating answer...")

            try:
                answer = generate_answer(question, context)
                print("\nAI:", answer, "\n")

            except Exception as error:
                print("\nError generating answer:", error)

    except Exception as error:
        print("\nAn error occurred:", error)


if __name__ == "__main__":
    main()