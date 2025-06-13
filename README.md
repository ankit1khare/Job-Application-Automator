# Job Application Automator

A Django-based web application that automates parsing resumes and applying to jobs via LinkedIn. It leverages LandingAI's Agentic Document Extraction (ADE) for accurate resume parsing and OpenAI's APIs for enhanced automation capabilities.

## Overview

Prototype app that automates the tedious aspects, allowing developers to invest more time in meaningful activities like analyzing job descriptions and strategically positioning their applications.

## Features

* **Resume Parsing:** Quickly and accurately parse resume PDFs into structured JSON data using LandingAI’s ADE.
* **LinkedIn Automation:** Automate job applications using parsed resume data through Playwright.
* **OpenAI Integration:** Utilize OpenAI’s Computer-Use and GPT-4 APIs for robust web automation and structured data extraction.

## Project Structure

```
job_application_automator/
├── users/                 # User authentication and profile management
│   ├── views.py           # User-related views
│   ├── models.py          # User models and custom auth
│   ├── forms.py           # Forms for user authentication
│   └── urls.py            # URL routes for user app
├── doc_parser/            # Resume parsing and LinkedIn automation
│   ├── views.py           # Handles file uploads and parsing
│   ├── models.py          # Stores parsed resume data
│   ├── utils.py           # Helper functions (LandingAI & OpenAI integration)
│   ├── operator_script.py # LinkedIn automation logic with Playwright
│   ├── linkedin_script.py # Additional LinkedIn utilities
│   └── urls.py            # URL routes for resume parsing
└── templates/             # HTML templates
    ├── users/             # User-related templates
    └── resume_parser/     # Resume-related templates
```

## Installation

Clone this repository:

```bash
git clone https://github.com/ankit1khare/Job-Application-Automator.git
cd job_application_automator
```

Create and activate virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Set environment variables:

```bash
export OPENAI_API_KEY="your_openai_api_key"
export VISION_AGENT_API_KEY="your_landingai_api_key"
export LINKEDIN_EMAIL="your_linkedin_email"
export LINKEDIN_PASSWORD="your_linkedin_password"
```

Run migrations and start the server:

```bash
python manage.py migrate
python manage.py runserver
```

## Usage

* **Sign Up/Login:** Visit `http://localhost:8000/users/register` to create your account.
* **Upload Resume:** Navigate to your dashboard to upload your resume.
* **Apply to Jobs:** Enter LinkedIn job URLs and let the automation handle the application process.

## How it Works

1. **Parsing resumes:** Uploaded resumes are parsed using LandingAI’s ADE to extract structured data.
2. **LinkedIn automation:** Using Playwright, the app fills in LinkedIn Easy Apply forms automatically.
3. **OpenAI APIs:**

   * **Computer-Use API:** Facilitates automatic web interaction with LinkedIn.
   * **GPT-4 API:** Ensures resume data is structured and accurate.

## Next Steps

This project currently automates basic job application tasks. You can further enhance it by integrating AI-driven analysis of job descriptions to suggest personalized improvements to applications.

## Resources

* [LandingAI ADE API](https://landing.ai/agentic-apis)
* [Agentic Document Extraction SDK](https://github.com/landing-ai/agentic-doc)
* [Playwright Documentation](https://playwright.dev/python/)
* [OpenAI API](https://platform.openai.com/docs/api-reference)

## Community

Join the conversation and share your innovative workflows using `#AgenticDoc` on social media and connect with our community on [Discord](https://discord.gg/RVcW3j9RgR).

## Contributing

Contributions are welcome! Please open an issue or submit a pull request to propose changes.

## License

Distributed under the MIT License.
