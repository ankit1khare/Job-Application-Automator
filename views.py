from django.shortcuts import render, redirect
from .models import Resume
from django.conf import settings
import io
import json
import requests
import openai
from .utils import *
from django.contrib import messages

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from users.forms import JobApplicationForm
from .operator_script import LinkedInOperatorAutomation
from threading import Thread
from asgiref.sync import sync_to_async
import tempfile
from agentic_doc.parse import parse_documents

def call_api_from_path(pdf_path):
    results = parse_documents([pdf_path])
    parsed_doc = results[0]
    
    return {
        "markdown": parsed_doc.markdown
    }

def upload_resume(request):
    if request.method == "POST":
        pdf_file = request.FILES.get("resume")
        pdf_bytes = pdf_file.read()
        print("hello i am inside the upload resume")

        with tempfile.NamedTemporaryFile(delete=True, suffix=".pdf") as tmp:
            tmp.write(pdf_bytes)
            tmp.flush()
            
            raw_data = call_api_from_path(tmp.name)

        print(f"raw data = {raw_data}")

        structured_data = extract_structured_resume(raw_data)
        resume = Resume.objects.create(user=request.user, original_pdf=pdf_file, parsed_data=structured_data)

        return redirect("dashboard")
    return redirect("dashboard")

    
def resume_detail(request, pk):
    resume = Resume.objects.get(pk=pk)
    pdf_view = display_pdf(resume.original_pdf.path)
    return render(request, "resume_parser/resume_detail.html", {"resume": resume, "pdf_view": pdf_view})

def save_resume(request, pk):
    resume = Resume.objects.get(pk=pk)

    parsed = {}

    parsed["name"] = request.POST.get("name")
    parsed["summary"] = request.POST.get("summary")

    parsed["contact"] = {
        "email": request.POST.get("email"),
        "phone": request.POST.get("phone"),
        "linkedin": request.POST.get("linkedin"),
        "github": request.POST.get("github"),
    }

    parsed["skills"] = request.POST.get("skills", "").split(",")

    parsed["education"] = []
    degrees = request.POST.getlist("degree")
    institutions = request.POST.getlist("institution")
    years = request.POST.getlist("year")
    for d, i, y in zip(degrees, institutions, years):
        parsed["education"].append({
            "degree": d,
            "institution": i,
            "year": y
        })

    parsed["experience"] = []
    titles = request.POST.getlist("experience_title")
    companies = request.POST.getlist("experience_company")
    durations = request.POST.getlist("experience_duration")
    for t, c, d in zip(titles, companies, durations):
        parsed["experience"].append({
            "job_title": t,
            "company": c,
            "duration": d
        })

    parsed["projects"] = []
    project_names = request.POST.getlist("project_name")
    project_descs = request.POST.getlist("project_description")
    for n, d in zip(project_names, project_descs):
        parsed["projects"].append({
            "name": n,
            "description": d
        })

    parsed["certifications"] = request.POST.get("certifications", "").split(",")
    parsed["languages"] = request.POST.get("languages", "").split(",")

    resume.parsed_data = parsed
    resume.save()
    messages.success(request, "Resume updated successfully!")
    return redirect("/dashboard/?toast=resume_uploaded")

def dashboard(request):
    resume = Resume.objects.filter(user=request.user).order_by("-created_at").first()
    pdf_preview = display_pdf(resume.original_pdf.path) if resume else None
    return render(request, "users/dashboard.html", {"resume": resume, "pdf_preview": pdf_preview})


def run_linkedin_automation(email, password, job_url, resume_data, latest_resume):
    try:
        bot = LinkedInOperatorAutomation(email, password, job_url, resume_data, latest_resume)
        bot.login_and_apply()
    except Exception as e:
        print("Error running automation:", e)

def job_apply_url(request):
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            job_url = form.cleaned_data['job_url']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                latest_resume = Resume.objects.filter(user=request.user).latest('created_at')
                resume_data = latest_resume.parsed_data
                print(f"Resume data: {resume_data}")

                Thread(target=run_linkedin_automation, args=(email, password, job_url, resume_data, latest_resume)).start()

                messages.success(request, "Job application process started in background.")
                return redirect('dashboard')

            except Resume.DoesNotExist:
                messages.error(request, "No resume found. Please upload one first.")
        else:
            messages.error(request, "There was an error with your form submission.")
    else:
        form = JobApplicationForm()

    return render(request, 'users/apply_to_job.html', {'form': form})