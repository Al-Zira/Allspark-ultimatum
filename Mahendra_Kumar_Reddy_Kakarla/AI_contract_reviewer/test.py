import google.generativeai as genai

genai.configure(api_key="AIzaSyDlVWvKtxMoPST4y2uySiibTiKx9-jkTS8")
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content("Write a short story about a robot learning to love.")

print(response.text)