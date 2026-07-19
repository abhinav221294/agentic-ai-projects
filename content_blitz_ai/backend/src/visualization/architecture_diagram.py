from content_blitz_ai.backend.src.workflows.content_workflow import __build_workflow

app = __build_workflow()

graph = app.get_graph()

print(graph.draw_ascii())

png_bytes = app.get_graph().draw_mermaid_png()

with open("content_blitz_architecture.png", "wb") as f:
    f.write(png_bytes)