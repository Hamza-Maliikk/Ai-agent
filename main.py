from ollama import chat

instruction_prompt = "You are a smart agent."

messages = [
    {"role": "system", "content": instruction_prompt}
]

while True:
    input_query = input("\n User: ")
    
    if "exit" in input_query.lower():
        print("Byee! Take care.")
        break
    
    messages.append({"role": "user", "content": input_query})
    
    response = chat(
        model='minimax-m3:cloud',
        messages=messages,
    )
    
    reply = response.message.content
    
    # agent ka reply bhi history mein daalo
    messages.append({"role": "assistant", "content": reply})
    
    print(f"\nAgent: {reply}")