import json
import gradio as gr

# JSON file path
json_file_path = r"learning_paths\frontend.json"

# Load the JSON data
def load_data():
    with open(json_file_path, "r") as file:
        return json.load(file)

# Save updated progress back to the JSON file
def save_progress(updated_steps):
    with open(json_file_path, "w") as file:
        json.dump(updated_steps, file, indent=4)

# Update task progress in JSON
def update_progress(selected_tasks):
    steps = load_data()

    # Update "completed" status based on selected tasks
    for step in steps["steps"]:
        for task in step["tasks"]:
            task["completed"] = task["title"] in selected_tasks

    save_progress(steps)

    # Calculate progress
    completed_tasks, total_tasks, progress = calculate_progress(steps)
    return f"Progress: Completed {completed_tasks}/{total_tasks} tasks ({progress}%)"

# Calculate progress percentage
def calculate_progress(steps):
    total_tasks = 0
    completed_tasks = 0
    for step in steps["steps"]:
        for task in step["tasks"]:
            if "completed" in task and task["completed"]:
                completed_tasks += 1
            total_tasks += 1
    progress = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
    return completed_tasks, total_tasks, progress

# Create a Gradio interface with hierarchical display
def create_interface():
    steps = load_data()

    with gr.Blocks() as demo:
        gr.Markdown("# Personalized Learning Path")
        gr.Markdown("### Track your progress step by step:")

        selected_tasks = []

        # Create a collapsible section for each step
        for step in steps["steps"]:
            with gr.Accordion("", open=True):
                gr.Markdown(f"**{step['title']}:**")
                gr.Markdown(f"**Description:** {step['description']}")

                # Show tasks with checkboxes
                task_titles = [task["title"] for task in step["tasks"]]
                completed_tasks = [
                    task["title"] for task in step["tasks"] if task.get("completed", False)
                ]
                checkboxes = gr.CheckboxGroup(
                    choices=task_titles, value=completed_tasks, label="Tasks"
                )
                selected_tasks.append(checkboxes)

        # Display progress and save button
        progress_display = gr.Label(value=f"Progress: {calculate_progress(steps)[2]}%")
        save_button = gr.Button("Save Progress")

        # When the save button is clicked, update the progress
        save_button.click(
            fn=lambda *task_lists: update_progress(
                [item for sublist in task_lists for item in sublist]
            ),
            inputs=selected_tasks,
            outputs=progress_display,
        )

    demo.launch()

# Run the application
if __name__ == "__main__":
    create_interface()
