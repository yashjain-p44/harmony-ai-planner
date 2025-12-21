"""Script to visualize the agent graph using the graph visualizer utility."""

from app.ai_agent.graph import create_agent
from app.ai_agent.util.graph_visualizer import display_graph, visualize_graph


def generate_graph_image(output_path: str = "agent_graph.png") -> None:
    """
    Generate an image of the compiled agent graph.
    
    Args:
        output_path: Path where to save the graph image. Defaults to "agent_graph.png"
    """
    # Create and compile the graph
    compiled_graph = create_agent()
    
    # Generate and display the graph image
    print(f"Generating graph visualization...")
    display_graph(compiled_graph, output_path=output_path)


def show_graph() -> None:
    """
    Display the agent graph inline (for Jupyter/IPython notebooks).
    """
    # Create and compile the graph
    compiled_graph = create_agent()
    
    # Display the graph
    display_graph(compiled_graph)


if __name__ == "__main__":
    # When run as a script, generate and save the graph image
    generate_graph_image()

