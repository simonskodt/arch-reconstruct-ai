"""
This file defines an email assistant agent for LangGraph Studio.
It uses LangChain and OpenAI to create an agent that can send emails via the send_email tool.
"""
from langchain.agents import create_agent

def send_email(to: str, subject: str, body: str):
    """Send an email"""
    email = {
        "to": to,
        "subject": subject,
        "body": body
    }
    print(email)
    # ... email sending logic

    return f"Email sent to {to}"

agent = create_agent(
    "openai:gpt-4.1-nano",
    tools=[send_email],
    prompt="Act as an email assistant. Use the send_email tool to send emails.",
)
