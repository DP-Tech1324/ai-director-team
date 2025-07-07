from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama-local"
)

res = client.chat.completions.create(
    model="phi3",
    messages=[{"role": "user", "content": "Say hello from Ollama"}]
)

print(res.choices[0].message.content)