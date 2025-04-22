from google import genai
import bot.load_config as load_config

client = genai.Client(api_key=load_config.gemini_api_key)


def fetch_gemini_response(text: str):

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=text,
    )
    with open("response.md", "w") as f:
        f.write(response.text)
    return response.text
