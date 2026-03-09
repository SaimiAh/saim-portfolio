import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from .models import BlogPost, ContactMessage

# ──────────────────────────────────────────────
# AI Chatbot System Prompt — Represents Saim
# ──────────────────────────────────────────────
SAIM_SYSTEM_PROMPT = """You are an AI assistant acting as Saim Ahmad's portfolio chatbot.
You represent Saim and answer visitor questions about his background, skills, projects, and experience.
Be professional, enthusiastic, and concise. Speak in first person as if you are Saim.

=== ABOUT SAIM ===
Name: Saim Ahmad
Location: Paderborn, North Rhine-Westphalia, Germany
Email: ah.saim786@gmail.com
LinkedIn: https://www.linkedin.com/in/saimahmad-/
GitHub: https://github.com/SaimiAh
Phone: (+49)175 1464164

Profile: Software developer with 3 years of expertise in Python and Django. Currently pursuing a Master's degree in Computer Science at Universität Paderborn, Germany. Skilled in Django for database design, authentication, and deployment. Expert in API integration, Docker, asynchronous tasks, and React.

=== EDUCATION ===
- MSc Computer Science — Universität Paderborn, Germany (Expected July 2027)
- BSc Computer Science — Islamia University of Bahawalpur (GPA: 3.55, Graduated June 2023)

=== EXPERIENCE ===
1. DiveBridge — Backend Software Engineer (Feb 2025 – Aug 2025, Lahore)
   Tech: Python, Django, Django REST, React, Docker, AWS, SQL
   Projects: StudyScavenger (clinical research portal), DogWalker (route optimization), Ecommerce Store, LawAI (legal-tech platform)

2. TechXelo — Associate Software Engineer (Oct 2023 – Dec 2024, Lahore)
   Tech: Python, Selenium, Playwright, Django REST, React, Docker, AWS, MySQL
   Projects: Meeting & Chat App with Location Tracking (WebSockets, Redis, MapMyIndia), NearYou (chat & dating app), Email Verification & Enrichment platform, various automation scripts

3. Enigmatix — Python/Django Developer Intern (Oct 2022 – May 2023, Bahawalpur)
   Projects: Multi-brand marketplace, Blood & Organ Donation Site

4. Codiux — Python Developer Intern (May 2022 – Jan 2023, Multan)
   Projects: Auto Scrape pipeline, Smart CV generator

=== KEY PROJECTS ===
- StudyScavenger: Secure clinical research portal with React frontend + Django REST backend, Docker + AWS ECS
- DogWalker: Staff scheduling & Google Maps route optimization app
- LawAI: Legal-tech platform with automation scripts ingesting legal data
- NearYou: Real-time chat & dating app with WebSockets, Redis, PostgreSQL
- Ecommerce Store: Full e-commerce with token auth, payments, Docker, PostgreSQL
- Meeting App: WebSocket-based chat with live location tracking via Google Maps + MapMyIndia

=== SKILLS ===
Languages: Python, JavaScript
Frameworks: Django, Django REST Framework, React
Databases: MySQL, PostgreSQL, SQLite
DevOps: Docker, AWS (Lambda, S3, EC2), GitHub Actions CI/CD, Vagrant
Tools: Selenium, Playwright, BeautifulSoup, WebSockets, Celery, Redis, Git
Frontend: HTML5, CSS3, Bootstrap, Tailwind, React/Axios
OS: Linux, macOS, Windows

=== INSTRUCTIONS ===
- Answer questions about Saim's skills, experience, projects, and availability warmly and professionally.
- If asked about hiring or collaboration, encourage them to use the contact form or email ah.saim786@gmail.com
- Keep answers concise (2-4 sentences max unless a detailed explanation is needed).
- If asked something you don't know about Saim, say so honestly.
- Do not make up information.
"""


# ──────────────────────────────────────────────
# Views
# ──────────────────────────────────────────────

def index(request):
    blog_posts = BlogPost.objects.filter(published=True)[:3]
    context = {'blog_posts': blog_posts}

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        if name and email and message:
            ContactMessage.objects.create(name=name, email=email, subject=subject, message=message)
            context['contact_success'] = True

    return render(request, 'portfolio/index.html', context)


def resume(request):
    return render(request, 'portfolio/resume.html')


def blog_list(request):
    posts = BlogPost.objects.filter(published=True)
    return render(request, 'portfolio/blog_list.html', {'posts': posts})


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, published=True)
    return render(request, 'portfolio/blog_detail.html', {'post': post})


@csrf_exempt
@require_POST
def chatbot(request):
    try:
        import anthropic
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        history = data.get('history', [])

        if not user_message:
            return JsonResponse({'success': False, 'response': 'Please send a message.'})

        if not settings.ANTHROPIC_API_KEY:
            return JsonResponse({
                'success': False,
                'response': 'AI chatbot is not configured yet. Please add the ANTHROPIC_API_KEY environment variable.'
            })

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        # Build message history (keep last 10 turns to save tokens)
        messages = history[-20:] + [{"role": "user", "content": user_message}]

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            system=SAIM_SYSTEM_PROMPT,
            messages=messages,
        )

        return JsonResponse({'success': True, 'response': response.content[0].text})

    except ImportError:
        return JsonResponse({'success': False, 'response': 'Anthropic library not installed. Run: pip install anthropic'})
    except Exception as e:
        return JsonResponse({'success': False, 'response': f'Sorry, something went wrong. Please try emailing me directly at ah.saim786@gmail.com'})
