p = print
from os import system as o
import google.generativeai as genai
from IPython.display import display
from IPython.display import Markdown
import json as j

with open("GOOGLE_API_KEY.json", "r") as f:
    GOOGLE_API_KEY = j.load(f)["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

for m in genai.list_models():
  if 'generateContent' in m.supported_generation_methods:
    print(m.name)

model = genai.GenerativeModel('gemini-1.5-pro-latest')

def chat(text):
  
  try:
      r = model.generate_content(text)
  except Exception as e:
      r = model.generate_content("Rephrase: im sorry but i cannot assist with that")
    
  return r.text.replace("*", "")
