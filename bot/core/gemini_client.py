from google import genai
import bot.load_config as load_config

client = genai.Client(api_key=load_config.gemini_api_key)

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="what are the best books to read for self help and growing",
)

with open("response.md", "w") as f:
    data = response.text
    f.write(data)
