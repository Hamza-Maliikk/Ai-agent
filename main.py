from ollama import chat
import requests
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
Model = "minimax-m3:cloud"

def send_chat_email(chat_history: list):
    sender = "hamzamalik123450@gmail.com"
    password = "alrf qwet fxbg ypxh"  # Gmail App Password
    
    body = "\n".join([
        f"{m['role'].upper()}: {m['content']}" 
        for m in chat_history 
        if m['role'] in ('user', 'assistant')
    ])
    
    msg = MIMEMultipart()
    msg["Subject"] = "Tumhari Chat Summary"
    msg["From"] = sender
    msg["To"] = "humzamalik@yopmail.com"
    msg.attach(MIMEText(body, "plain"))
    
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as server:
        server.login(sender, password)
        server.sendmail(sender, msg["To"], msg.as_string())
    print("✅ Email bheji gayi!")

def calculate(expression: str) -> str:
    try:
        result = eval(expression)
        return str(result)
    except:
        return "Calculation is wrong"


def get_weather(city):
    geo = requests.get(
        f"http://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
    ).json()
    if not geo.get("results"):
        return f"{city} nahi mila"
    loc = geo["results"][0]
    w = requests.get(
        f"http://api.open-meteo.com/v1/forecast?latitude={loc['latitude']}&longitude={loc['longitude']}"
        f"&current=temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m&timezone=auto").json()["current"]
    return f"{loc['name']} weather: {w['temperature_2m']}°C, feels {w['apparent_temperature']}°C, humidity {w['relative_humidity_2m']}%, wind {w['wind_speed_10m']} km/h"


tools = [
    {
        "type": "function",
        "function": {
            "name": "send_chat_email",
            "description": "Chat history ka email bhejne ke liye",
            "parameters": {
                "type": "object",
                "properties": {
                    "chat_history": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "role": {"type": "string"},
                                "content": {"type": "string"},
                            },
                            "required": ["role", "content"],
                        },
                    }
                },
                "required": ["chat_history"],
            },
        },
    }
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "calculate",
    #         "description": "Maths calculate karta hai — jab user koi calculation maange",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "expression": {
    #                     "type": "string",
    #                     "description": "Math expression jaise 2+2 ya 10*5",
    #                 }
    #             },
    #             "required": ["expression"],
    #         },
    #     },
    # },
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "email_user",
    #         "description": "taking user email",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "email": {
    #                     "type": "string",
    #                     "description": "User's email address"
    #                 }
    #             },
    #             "required": ["email"]
    #         }
    #     }
    # },
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "get_weather",
    #         "description": "Kisi city ka weather batata hai",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "city": {"type": "string", "description": "City ka naam"}
    #             },
    #             "required": ["city"],
    #         },
    #     },
    # },
]

available_tools = {
    "calculate": calculate,
    # "email_user": email_user,
    "get_weather": get_weather,
}

instruction_prompt = "You are a smart lead generator agent. " \
"Your job is to generate high-quality leads for our sales team." \
"Ask the user name, email, phone number, and service they are interested in. " \
"it's neccessary that user give email or phone number" \
"in case user don't want to share name or phone or service proceed email without it" \
"but in case user not share email that's okay but the phone number is required" \
"once collect information proceed the email"

messages = [{"role": "system", "content": instruction_prompt}]

while True:
    input_query = input("\nTum: ")
    messages.append({"role": "user", "content": input_query})

    response = chat(  # ✅ fix — 4 spaces indentation
        model=Model, messages=messages, tools=tools
    )

    if response.message.tool_calls:
        messages.append(response.message)  # <<< YE LINE MISSING THI
        for tool_call in response.message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = tool_call.function.arguments

            print(f"\n[Tool use kar raha hai: {tool_name}]")

            tool_result = available_tools[tool_name](**tool_args)
            messages.append({"role": "tool", "content": tool_result})

        final_response = chat(model=Model, messages=messages, tools=tools)
        reply = final_response.message.content

    else:
        reply = response.message.content

    messages.append({"role": "assistant", "content": reply})
    print(f"\nAgent: {reply}")




