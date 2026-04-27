import os
from graph.workflow import app
from graphviz import Digraph
import os
from dotenv import load_dotenv
load_dotenv()

if os.getenv("GRAPHVIZ_PATH"):
    os.environ["PATH"] += os.pathsep + os.getenv("GRAPHVIZ_PATH")

def export_graph_png(filename="agent_workflow"):

    graph = app.get_graph()

    dot = Digraph()
    dot.attr(rankdir="TB", size="10,8")

    for node in graph.nodes:

        # Router (distinct)
        if node == "router_agent":
            dot.node(node, style="filled", fillcolor="lightgreen", shape="box")

        # All worker agents (same color)
        elif node in [
            "advisor_agent",
            "market_agent",
            "risk_agent",
            "news_agent",
            "rag_agent"
        ]:
            dot.node(node, style="filled", fillcolor="lightblue")

        # Fallback
        elif node == "fallback_agent":
            dot.node(node, style="filled", fillcolor="lightgrey")

        # Start / End
        elif "__start__" in node:
            dot.node(node, shape="circle")

        elif "__end__" in node:
            dot.node(node, shape="doublecircle")

        else:
            dot.node(node)

    # edges
    for edge in graph.edges:
        dot.edge(edge[0], edge[1])

    print("📁 Saving in:", os.getcwd())
    dot.render(filename, format="png", cleanup=True)

    print(f"✅ Graph saved as {filename}.png")