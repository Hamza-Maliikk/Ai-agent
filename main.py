from ollama import chat
import requests

Model = "minimax-m3:cloud"


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
            "name": "calculate",
            "description": "Maths calculate karta hai — jab user koi calculation maange",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression jaise 2+2 ya 10*5",
                    }
                },
                "required": ["expression"],
            },
        },
    },
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
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Kisi city ka weather batata hai",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City ka naam"}
                },
                "required": ["city"],
            },
        },
    },
]

available_tools = {
    "calculate": calculate,
    # "email_user": email_user,
    "get_weather": get_weather,
}

instruction_prompt = "You are a smart agent. Use tools when needed."
messages = [{"role": "system", "content": instruction_prompt}]

while True:
    input_query = input("\nTum: ")

    if "exit" in input_query.lower():
        print("Khuda Hafiz!")
        break

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
