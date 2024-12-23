import gradio as gr




def read_learning_path(file_path):
    learning_path = {}
    with open(file_path, 'r') as file:
        lines = file.readlines()
        current_category = None
        current_subcategory = None

        for line in lines:
            line = line.strip()
            if line.startswith("**"):  # Category
                current_category = line.replace("**", "").strip()
                learning_path[current_category] = {}
            elif line.startswith("*"):  # Subcategory
                current_subcategory = line.replace("*", "").strip()
                learning_path[current_category][current_subcategory] = []
            else:  # Steps
                if current_subcategory:
                    learning_path[current_category][current_subcategory].append(line)

    return learning_path

# Function to calculate progress
def calculate_progress(completed_steps):
    total_steps = sum(len(steps) for subcategory in learning_path.values() for steps in subcategory.values())
    completed_count = sum(1 for step in completed_steps if step in [s for subcategory in learning_path.values() for steps in subcategory.values() for s in steps])
    progress_percentage = (completed_count / total_steps) * 100 if total_steps > 0 else 0
    return f"Progress: {progress_percentage:.2f}%"

# Create the Gradio interface
def create_interface(learning_path):
    checkboxes = []
    for category, subcategories in learning_path.items():
        for subcategory, steps in subcategories.items():
            checkboxes.append(gr.CheckboxGroup(label=subcategory, choices=steps))

    with gr.Blocks() as demo:
        gr.Markdown("# Dynamic Learning Path Progress Tracker")
        completed_steps = gr.CheckboxGroup(label="Select Completed Steps", choices=[step for subcategory in learning_path.values() for steps in subcategory.values() for step in steps])
        progress_button = gr.Button("Calculate Progress")
        progress_output = gr.Textbox(label="Progress Output")

        progress_button.click(calculate_progress, inputs=completed_steps, outputs=progress_output)

    return demo

# Main execution
if __name__ == "__main__":
    file_path = r"learning_paths\fronend developer.txt"  # Update with your file path

    learning_path = read_learning_path(file_path)
    demo = create_interface(learning_path)
    demo.launch()