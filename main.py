
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
from urllib.parse import urlparse
from database import get_connection

app = FastAPI(title="Personal Portfolio")

# Static files
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

# Jinja2 configuration
templates = Jinja2Templates(directory="templates")


# Common context for all pages
def get_context(request: Request):
    return {
        "request": request,
        "theme": request.cookies.get("theme", "light"),
        "year": datetime.now().year
    }


# HOME PAGE
@app.get("/")
async def home(request: Request):
    context = get_context(request)

    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context=context
    )


# ABOUT PAGE
@app.get("/about")
async def about(request: Request):
    context = get_context(request)

    return templates.TemplateResponse(
        request=request,
        name="about.html",
        context=context
    )


# SKILLS PAGE
@app.get("/skills")
async def skills(request: Request):
    context = get_context(request)

    context["skills"] = [
        "Python", "Java", "FastAPI",
        "Spring Boot", "HTML", "CSS",
        "JavaScript", "React.js",
        "MySQL", "SQL", "Git",
        "Machine Learning"
    ]

    return templates.TemplateResponse(
        request=request,
        name="skills.html",
        context=context
    )


# PROJECTS PAGE
@app.get("/projects")
async def projects(request: Request):
    context = get_context(request)

    context["projects"] = [
    {
        "title": "ShapDrop",
        "description": "Python e-commerce application.",
        "tech": ["Python", "FastAPI", "MySQL"],
        "category": "python"
    },
    {
        "title": "TableTap",
        "description": "Restaurant ordering management system.",
        "tech": ["Java", "Spring Boot", "MySQL"],
        "category": "java"
    },
    {
        "title": "Recipe Recommendation System",
        "description": "AI-based recipe recommendation platform.",
        "tech": ["Python", "Machine Learning", "React"],
        "category": "ai"
    },
    {
        "title": "CodeLearn",
        "description": "Interactive programming learning platform.",
        "tech": ["React", "HTML", "CSS", "JavaScript"],
        "category": "frontend"
    }
]

    return templates.TemplateResponse(
        request=request,
        name="projects.html",
        context=context
    )


# EXPERIENCE PAGE
@app.get("/experience")
async def experience(request: Request):
    context = get_context(request)

    return templates.TemplateResponse(
        request=request,
        name="experience.html",
        context=context
    )


# CONTACT PAGE
@app.get("/contact")
async def contact(request: Request):
    context = get_context(request)
    return templates.TemplateResponse(
        request=request,
        name="contact.html",
        context=context
    )
@app.post("/contact")
async def submit_contact(request: Request):
    form = await request.form()

    name = form.get("name")
    email = form.get("email")
    subject = form.get("subject")
    message = form.get("message")

    if not all([name, email, subject, message]):
        context = get_context(request)
        context["error"] = "All fields are required."

        return templates.TemplateResponse(
            request=request,
            name="contact.html",
            context=context
        )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """INSERT INTO contacts (name, email, subject, message)
           VALUES (%s, %s, %s, %s)""",
        (name, email, subject, message)
    )

    conn.commit()
    cursor.close()
    conn.close()

    context = get_context(request)
    context["success"] = True

    return templates.TemplateResponse(
        request=request,
        name="contact.html",
        context=context
    )


# THEME SWITCHER
@app.post("/set-theme")
async def set_theme(request: Request):

    # 1. Read existing theme
    current_theme = request.cookies.get("theme", "light")

    # 2. Toggle theme
    new_theme = "dark" if current_theme == "light" else "light"

    # 3. Get previous page URL
    referer = request.headers.get("referer")

    # 4. Validate redirect URL
    redirect_url = "/"

    if referer:
        parsed_url = urlparse(referer)

        if parsed_url.netloc == request.url.netloc:
            redirect_url = parsed_url.path or "/"

            if parsed_url.query:
                redirect_url += "?" + parsed_url.query

    # 5. Create HTTP 303 redirect
    response = RedirectResponse(
        url=redirect_url,
        status_code=303
    )

    # 6. Store theme in browser cookie
    response.set_cookie(
        key="theme",
        value=new_theme,
        max_age=2592000,
        httponly=True,
        samesite="lax",
        path="/"
    )

    return response

@app.post("/contact")
async def submit_contact(request: Request):
    form_data = await request.form()

    name = form_data.get("name")
    email = form_data.get("email")
    subject = form_data.get("subject")
    message = form_data.get("message")

    if not all([name, email, subject, message]):
        context = get_context(request)
        context["success"] = False
        context["error"] = "Please fill in all fields."

        return templates.TemplateResponse(
            request=request,
            name="contact.html",
            context=context
        )

    context = get_context(request)
    context["success"] = True

    return templates.TemplateResponse(
        request=request,
        name="contact.html",
        context=context
    )

@app.get("/admin/messages")
async def admin_messages(request: Request):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM contacts ORDER BY id DESC")
    messages = cursor.fetchall()

    cursor.close()
    conn.close()

    context = get_context(request)
    context["messages"] = messages

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context=context
    )