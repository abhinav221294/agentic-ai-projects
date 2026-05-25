import os
from graph.workflow import app
from graphviz import Digraph
from dotenv import load_dotenv

load_dotenv()

# Add Graphviz to PATH if provided
if os.getenv("GRAPHVIZ_PATH"):
    os.environ["PATH"] += os.pathsep + os.getenv("GRAPHVIZ_PATH")


def export_graph_png(filename="agent_workflow"):

    graph = app.get_graph()

    dot = Digraph()

    # -------------------------
    # GLOBAL STYLING
    # -------------------------
    dot.attr(rankdir="TB")  # Top → Bottom
    dot.attr(size="10,8")
    dot.attr(splines="polyline")
    dot.attr(nodesep="0.6")
    dot.attr(ranksep="0.8")

    # -------------------------
    # NODES
    # -------------------------
    for node in graph.nodes:

        # Router
        if node == "router_agent":
            dot.node(node, style="filled", fillcolor="lightgreen", shape="box")

        # Worker agents
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
        elif node == "__start__":
            dot.node(node, shape="circle")

        elif node == "__end__":
            dot.node(node, shape="doublecircle")

        else:
            dot.node(node)

    # -------------------------
    # FORCE CLEAN LAYOUT (RANKS)
    # -------------------------
    with dot.subgraph() as s:
        s.attr(rank='same')
        s.node("__start__")

    with dot.subgraph() as s:
        s.attr(rank='same')
        s.node("router_agent")

    with dot.subgraph() as s:
        s.attr(rank='same')
        for agent in [
            "advisor_agent",
            "market_agent",
            "risk_agent",
            "news_agent",
            "rag_agent",
            "fallback_agent"
        ]:
            s.node(agent)

    with dot.subgraph() as s:
        s.attr(rank='same')
        s.node("__end__")

    # -------------------------
    # EDGES (FILTERED)
    # -------------------------
    for edge in graph.edges:
        if len(edge) >= 2:
            src = edge[0]
            dst = edge[1]
        else:
            continue

        # ❌ Remove fake router → end edge
        if src == "router_agent" and dst == "__end__":
            continue

        dot.edge(src, dst)

    # -------------------------
    # SAVE
    # -------------------------
    print("📁 Saving in:", os.getcwd())
    dot.render(filename, format="png", cleanup=True)

    print(f"✅ Graph saved as {filename}.png")