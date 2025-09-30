from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4.1-nano")

def send_email(to: str, subject: str, body: str):
    """Send an email"""
    email = {
        "to": to,
        "subject": subject,
        "body": body
    }
    # ... email sending logic

    return f"Email sent to {to}"

agent = create_agent(
    "openai:gpt-4.1-nano",
    tools=[send_email],
    prompt="Act as an email assistant. Use the send_email tool to send emails.",
)