import google.generativeai as genai
from secret import API_KEY

genai.configure(api_key=API_KEY)

for m in genai.list_models():
    print(m.name)