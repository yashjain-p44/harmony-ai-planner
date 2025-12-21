"""Utility for visualizing LangGraph compiled graphs using IPython.display."""

from IPython.display import Image, display
from typing import Any


def visualize_graph(compiled_graph: Any, output_path: str = None) -> Image:
    """
    Generate and display an image of a compiled LangGraph.
    
    Args:
        compiled_graph: A compiled LangGraph StateGraph
        output_path: Optional path to save the graph image. If None, displays inline.
        
    Returns:
        IPython.display.Image object of the graph visualization
    """
    try:
        # Get the graphviz representation from the compiled graph
        graph = compiled_graph.get_graph()
        
        # Generate the image bytes
        graph_image_bytes = graph.draw_mermaid_png()
        
        # If output_path is provided, save to file
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(graph_image_bytes)
            return Image(output_path)
        else:
            # Display inline using the bytes directly
            return Image(graph_image_bytes)
    except AttributeError:
        # Fallback: try alternative method if get_graph() doesn't exist
        try:
            # Some versions might use get_graph().draw_mermaid() or similar
            graph = compiled_graph.get_graph()
            if hasattr(graph, 'draw_mermaid_png'):
                graph_image_bytes = graph.draw_mermaid_png()
                if output_path:
                    with open(output_path, 'wb') as f:
                        f.write(graph_image_bytes)
                    return Image(output_path)
                else:
                    return Image(graph_image_bytes)
            elif hasattr(graph, 'draw_mermaid'):
                # Convert mermaid to image if needed
                mermaid_code = graph.draw_mermaid()
                # For now, return the mermaid code as text
                # In a full implementation, you'd convert mermaid to PNG
                print("Mermaid representation:")
                print(mermaid_code)
                return None
        except Exception as e:
            raise ValueError(f"Unable to visualize graph: {e}. Make sure the graph is compiled.")


def display_graph(compiled_graph: Any, output_path: str = None) -> None:
    """
    Display a compiled graph visualization inline in Jupyter/IPython.
    
    Args:
        compiled_graph: A compiled LangGraph StateGraph
        output_path: Optional path to save the graph image
    """
    image = visualize_graph(compiled_graph, output_path)
    if image:
        display(image)
    if output_path:
        print(f"Graph saved to: {output_path}")

