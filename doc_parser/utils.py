import io
import json
import base64
import os
import time
import requests
import openai
from django.conf import settings
from PyPDF2 import PdfReader, PdfWriter
import requests
import fitz  
# import openai
import json
from agentic_doc.parse import parse_documents
# from agentic_doc import LandingDocClient
# from agentic_doc.schema import ParseConfig
# from agentic_doc import LandingDocClient, ParseConfig




from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


from dotenv import load_dotenv
load_dotenv()

def call_api(pdf_path):
    results = parse_documents([pdf_path])
    parsed_doc = results[0]

    markdown_output = parsed_doc.markdown
    structured_chunks = parsed_doc.chunks

    return {
        "markdown": markdown_output,
        "chunks": structured_chunks
    }

def split_pdf_into_chunks(pdf_bytes, chunk_size=2): 
    print("in split")
    reader = PdfReader(io.BytesIO(pdf_bytes))
    chunks = []

    for start in range(0, len(reader.pages), chunk_size):
        writer = PdfWriter()
        for i in range(start, min(start + chunk_size, len(reader.pages))):
            writer.add_page(reader.pages[i])

        output_stream = io.BytesIO()
        writer.write(output_stream)
        chunks.append(output_stream.getvalue())
        print(f"Created chunk with pages {start + 1} to {min(start + chunk_size, len(reader.pages))}")

    return chunks


def call_landing_ai_api(pdf_chunk_bytes, retries=2, delay=5):
    url = "https://api.landing.ai/v1/tools/document-analysis"
    files = {"pdf": ("chunk.pdf", io.BytesIO(pdf_chunk_bytes), "application/pdf")}
    data = {
        "parse_text": True,
        "parse_tables": True,
        "parse_figures": True,
        "summary_verbosity": "none",
        "caption_format": "json",
        "response_format": "json",
        "return_chunk_crops": False,
        "return_page_crops": False,
    }
    headers = {"Authorization": f"Basic {settings.LANDING_AI_API_KEY}"}

    for attempt in range(retries):
        try:
            response = requests.post(url, files=files, data=data, headers=headers, timeout=160)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            if attempt < retries - 1:
                print(f"Timeout occurred, retrying {attempt + 1}/{retries}...")
                time.sleep(delay)
            else:
                return {"error": "API request timed out after multiple attempts."}
        except requests.exceptions.RequestException as e:
            return {"error": "API request failed.", "details": str(e)}

def call_api_for_full_pdf(pdf_bytes):
    try:
        chunks = split_pdf_into_chunks(pdf_bytes)
        all_data = []

        for idx, chunk_bytes in enumerate(chunks):
            print(f"Processing chunk {idx + 1}/{len(chunks)}")
            response = call_landing_ai_api(chunk_bytes)
            if "error" in response:
                return {"error": f"Failed on chunk {idx + 1}", "details": response}
            all_data.extend(response.get("data", {}).get("pages", []))  # accumulate parsed chunks

        return {
            "data": {
                "pages": all_data,
                "total_chunks": len(chunks)
            }
        }

    except Exception as e:
        return {
            "error": "Error processing PDF.",
            "details": str(e)
        }


def extract_structured_resume(raw_data):
    markdown_text = raw_data.get("markdown", "")
    
    prompt = f"""
    Extract structured resume data from the following Markdown content.

    Return only a valid JSON object (not in markdown format, without any wrapping backticks) in the following structure:
    {{
        "name": "Full name of the candidate",
        "contact": {{
            "email": "example@email.com",
            "phone": "1234567890",
            "LinkedIn": "...",
            "GitHub": "...",
            ...
        }},
        "education": [
            {{"degree": "...", "institution": "...", "year": "..."}},
            ...
        ],
        "skills": ["..."],
        "experience": [
            {{
                "job_title": "...",
                "company": "...",
                "duration": "...",
                "description": "..."
            }},
            ...
        ],
        "projects": [
            {{"name": "...", "description": "..."}},
            ...
        ],
        "certifications": ["..."],
        "languages": ["..."],
        "summary": "...",
        "extras": {{
            "awards": "...",
            "volunteering": "...",
            ...
        }}
    }}

    Markdown Resume:
    {markdown_text}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Extract structured resume data from markdown for use in job portals and databases."},
                {"role": "user", "content": prompt}
            ]
        )
        structured_data = response.choices[0].message.content.strip()

        print("OpenAI API Response (raw):", structured_data)

        # Clean up any accidental markdown formatting
        if structured_data.startswith("```json"):
            structured_data = structured_data[7:]
        if structured_data.endswith("```"):
            structured_data = structured_data[:-3]

        print("OpenAI API Response (cleaned):", structured_data)
        return json.loads(structured_data)

    except Exception as e:
        print(f"Error while calling OpenAI API: {str(e)}")
        return {}




def display_pdf(pdf_path):
    if not os.path.exists(pdf_path):
        return f"<p class='text-danger'>Resume file not found. Please upload again.</p>"
    
    with open(pdf_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    return f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600px" style="border:1px solid #ccc; border-radius:6px;"></iframe>'
    
def extract_text_from_pdf(pdf_bytes):
    """
    Extract text from a PDF using PyMuPDF (supports any number of pages)
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    return "\n".join([page.get_text() for page in doc])


# def extract_structured_resume_from_text(resume_text):
    """
    Use OpenAI to extract structured resume data from raw text
    """
    prompt = f"""
            Extract all relevant information from the following resume text.
            Respond with only the JSON object, without markdown formatting.

            Return a JSON object with these fields:
            - name: Full name of the candidate
            - contact: Dictionary of all contact methods like email, phone, LinkedIn, GitHub, Twitter, portfolio, etc.
            - education: List of {{"degree", "institution", "year"}}
            - skills: List of technical and soft skills
            - experience: List of {{"job_title", "company", "duration", "description"}}
            - projects: List of {{"name", "description"}}
            - certifications: List of certifications or licenses
            - languages: List of known languages (with proficiency if available)
            - summary: Professional summary or objective statement
            - extras: A dictionary of any additional sections not listed above (e.g., awards, volunteering, publications, hobbies, courses), where the key is the section title and the value is a free-form or list

            Only return a valid JSON object without markdown formatting.

            Resume Text:
            {resume_text}
            """



    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are an expert resume parser."},
            {"role": "user", "content": prompt}
        ]
    )

    content = response["choices"][0]["message"]["content"]
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        print("Failed to parse JSON. Raw output:\n", content)
        return {"error": "Invalid JSON returned by OpenAI", "raw_output": content}

def extract_structured_resume_from_text(resume_text):
    """
    Use OpenAI to extract structured resume data from raw text
    """
    prompt = f"""
            Extract all relevant information from the following resume text.
            Respond with only the JSON object, without markdown formatting.

            Return a JSON object with these fields:
            - name: Full name of the candidate
            - contact: Dictionary of all contact methods like email, phone, LinkedIn, GitHub, Twitter, portfolio, etc.
            - education: List of {{"degree", "institution", "year"}}
            - skills: List of technical and soft skills
            - experience: List of {{"job_title", "company", "duration", "description"}}
            - projects: List of {{"name", "description"}}
            - certifications: List of certifications or licenses
            - languages: List of known languages (with proficiency if available)
            - summary: Professional summary or objective statement
            - extras: A dictionary of any additional sections not listed above (e.g., awards, volunteering, publications, hobbies, courses), where the key is the section title and the value is a free-form or list

            Only return a valid JSON object without markdown formatting.

            Resume Text:
            {resume_text}
            """

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are an expert resume parser."},
            {"role": "user", "content": prompt}
        ]
    )

    content = response.choices[0].message.content
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        print("Failed to parse JSON. Raw output:\n", content)
        return {"error": "Invalid JSON returned by OpenAI", "raw_output": content}
