from groq import Groq
import json
groq_api=st.secrets["groq_api_key"]

def extract_profile_from_chat(chat_text):
    client = Groq(
        api_key=groq_api,
    )
    prompt = f"""
    Extract the following fields from the chat below:
    - location
    - preferred cuisine
    - budget (Budget, Mid-range, Luxury)

    Chat: \"\"\"{chat_text}\"\"\"

    Return response in JSON:
    {{
      "location": "...",
      "cuisine": "...",
      "budget": "...",
    }}
    """

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        model="llama3-8b-8192",
        max_tokens=1024,
        response_format={"type": "json_object"},
    )

    content = chat_completion.choices[0].message.content
    return json.loads(content)

def get_intent_from_llm(query,prompt):
    client = Groq(
        api_key=groq_api,
    )
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"{prompt}"
            },
            {
                "role": "user",
                "content": f"{query} ",
            }
        ],
        model="llama3-8b-8192",
        max_tokens=1024
    )
    sum_cont = chat_completion.choices[0].message.content
    response=sum_cont
    return response
