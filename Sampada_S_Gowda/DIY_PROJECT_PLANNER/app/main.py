import os
import time
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up Gemini API key
api_key = os.getenv("GEMINI_API_KEY")
if api_key is None:
    raise ValueError("API key not found. Please set GEMINI_API_KEY in the .env file.")

# Configure Gemini API
genai.configure(api_key=api_key)

# Initialize the Gemini model
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# Helper function for currency conversion
def usd_to_inr(usd, rate=83):
    return round(usd * rate, 2)

def inr_to_usd(inr, rate=83):
    return round(inr / rate, 2)

# Logic for project planning
saved_projects = []  # List to store saved projects

def generate_project(skill_level, budget_value, currency, interests, user_prompt):
    if currency == "USD":
        budget_usd = budget_value
        budget_inr = usd_to_inr(budget_value)
    elif currency == "INR":
        budget_inr = budget_value
        budget_usd = inr_to_usd(budget_value)
    else:
        return "Invalid currency selection."

    prompt = (
        f"Suggest a {skill_level} level DIY project for someone interested in {interests}. "
        f"The budget is ${budget_usd} (₹{budget_inr}). "
        f"Additionally, address this request: '{user_prompt}' in a safe, non-dangerous way. "
        f"Provide detailed steps, tools, and materials needed."
    )

    try:
        response = model.generate_content(prompt)
        # Remove "*" symbols from the response text
        return response.text.strip().replace("*", "")
    except Exception as e:
        return f"Error generating project plan: {e}"

def save_project(skill_level, budget_value, currency, interests, user_prompt, plan):
    if not plan.strip():
        return "No project plan to save."

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    project_title = f"{skill_level} DIY Project: {interests.capitalize()} (Budget: ${budget_value}/₹{round(budget_value * 83, 2)})"
    saved_projects.append({
        "title": project_title,
        "skill_level": skill_level,
        "timestamp": timestamp,
        "plan": plan,
    })
    return f"Project saved! Total saved projects: {len(saved_projects)}"

def view_projects():
    if not saved_projects:
        return ["No saved projects yet."]
    return [f"{i + 1}. {project['title']}" for i, project in enumerate(saved_projects)]

def show_project_details(project_number):
    try:
        project = saved_projects[project_number - 1]  # Convert number to index
        return project["plan"]
    except IndexError:
        return "Project not found."

def download_project_details(project_number):
    try:
        project = saved_projects[project_number - 1]  # Convert number to index
        project_details = f"Title: {project['title']}\n\nPlan:\n{project['plan']}"
        return project_details
    except IndexError:
        return "Project not found."

# Function to stream text letter by letter
def stream_text(text, delay=0.1):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()  # To move to the next line after streaming

# Terminal-based interaction
def terminal_interface():
    while True:
        print("\nDIY Project Planner")
        print("1. Generate Project Plan")
        print("2. View Saved Projects")
        print("3. Show Project Details")
        print("4. Download Project Details")
        print("5. Exit")
        
        choice = input("Choose an option: ")

        if choice == "1":
            skill_level = input("Enter skill level (Beginner, Intermediate, Expert): ")
            budget_value = float(input("Enter budget value: "))
            currency = input("Enter currency (USD, INR): ")
            interests = input("Enter interests (e.g., woodworking, crafts): ")
            user_prompt = input("Enter custom prompt (e.g., specific project idea): ")

            plan = generate_project(skill_level, budget_value, currency, interests, user_prompt)
            print("\nGenerated Project Plan:")
            stream_text(plan)  # Streaming the plan text

            save_option = input("\nDo you want to save this project? (y/n): ")
            if save_option.lower() == "y":
                save_status = save_project(skill_level, budget_value, currency, interests, user_prompt, plan)
                print(save_status)

        elif choice == "2":
            projects = view_projects()
            print("\nSaved Projects:")
            for project in projects:
                print(project)

        elif choice == "3":
            try:
                project_number = int(input("Enter the project number to view details: "))
                details = show_project_details(project_number)
                print("\nProject Details:")
                stream_text(details)  # Streaming the project details
            except ValueError:
                print("Invalid input. Please enter a valid project number.")

        elif choice == "4":
            try:
                project_number = int(input("Enter the project number to download details: "))
                details = download_project_details(project_number)
                if details == "Project not found.":
                    print(details)
                else:
                    with open(f"project_{project_number}.txt", "w") as file:
                        file.write(details)
                    print(f"\nProject details saved as project_{project_number}.txt")
            except ValueError:
                print("Invalid input. Please enter a valid project number.")

        elif choice == "5":
            print("Exiting...")
            break

        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    terminal_interface()
