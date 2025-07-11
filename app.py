import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import uvicorn


load_dotenv()

config = ConnectionConfig(
    MAIL_USERNAME = os.getenv("SENDER_EMAIL"),
    MAIL_PASSWORD = os.getenv("EMAIL_PASSWORD"),
    MAIL_FROM = os.getenv("SENDER_EMAIL"),
    MAIL_PORT = int(os.getenv("PORT")),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=os.getenv("MAIL_STARTTLS") == "True",
    MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS") == "True",
    USE_CREDENTIALS=True
)

# class EmailSchema(BaseModel):
#     email: EmailStr
#     subject: str
#     body: str

app = FastAPI()

templates = Jinja2Templates(directory = "templates")

@app.post("/send_email")
async def send_email(
    email: EmailStr = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    checkbox: Optional[str] = Form(None)):

    if checkbox is not None:
        message = MessageSchema(subject=f"Email from {subject}", recipients=[email], body=body, subtype="plain")
        mail = FastMail(config)
        await mail.send_message(message)

    message = MessageSchema(subject=f"Feedback from {subject}", recipients=[os.getenv("ADMIN_EMAIL")], body=body, subtype="plain")
    mail = FastMail(config)
    await mail.send_message(message)
    
    return RedirectResponse(url = f"/thank_you?name={subject}", status_code = 302)


@app.get("/", response_class = HTMLResponse)
def home_page(request: Request):
    return templates.TemplateResponse("feedback.html", {"request": request})

@app.get("/thank_you", response_class=HTMLResponse)
def thank_you(request: Request, name: str):
    return templates.TemplateResponse("thankyou.html", {"request": request, "name": name})


if __name__ == '__main__':
    uvicorn.run("app:app", host = "0.0.0.0", port = 8000, reload = True)