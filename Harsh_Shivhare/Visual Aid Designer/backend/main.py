from mermaid_renderer import MermaidRenderer
from diagram_generator import generate_mermaid_code, get_diagram_prompt

def main():
    # Supported diagram types
    supported_diagram_types = [
        "flowchart-diagram",
        "sequence-diagram",
        "class-diagram",
        "state-diagram",
        "entity-relationship-diagram",
        "gantt-diagram",
        "pie-chart",
        "quadrant-chart",
        "reqirement-diagram",
        "timeline-diagram",
        "git-diagram",
        "mind-map-diagram"
    ]

    # Display diagram type options
    print("Select a diagram type:")
    for idx, diagram_type in enumerate(supported_diagram_types, start=1):
        print(f"{idx}. {diagram_type}")
    print(f"{len(supported_diagram_types) + 1}. Exit")

    # Get user choice
    choice = input("Enter the number corresponding to your choice: ")

    if choice == str(len(supported_diagram_types) + 1):
        print("Exiting the program.")
        return

    try:
        choice_idx = int(choice) - 1
        if choice_idx < 0 or choice_idx >= len(supported_diagram_types):
            raise ValueError
        selected_diagram_type = supported_diagram_types[choice_idx]
    except ValueError:
        print("Invalid choice. Please enter a valid number.")
        return

    # Get user input for the diagram
    user_input = input("Enter the details for the diagram: ")

    # Generate Mermaid code
    try:
        mermaid_code = generate_mermaid_code(selected_diagram_type, user_input)
        print("\nGenerated Mermaid.js Code:\n", mermaid_code)
    except Exception as e:
        print(f"Error generating Mermaid code: {e}")
        return

    # Render the diagram
    renderer = MermaidRenderer()
    output_path = f"{selected_diagram_type}_diagram.png"
    success = renderer.render_diagram(mermaid_code, output_path)

    if success:
        print(f"\nDiagram successfully generated at: {output_path}")
    else:
        print("Failed to generate diagram.")

if __name__ == "__main__":
    main()