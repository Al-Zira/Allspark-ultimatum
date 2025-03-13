from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from diagram_generator import generate_mermaid_code
from mermaid_renderer import MermaidRenderer
import tempfile
import os
from fastapi.responses import FileResponse
from typing import Optional

app = FastAPI(title="Visual Aid Designer API")
renderer = MermaidRenderer()

class DiagramRequest(BaseModel):
    prompt: str
    diagram_type: str

class DiagramResponse(BaseModel):
    mermaid_code: str
    image_path: Optional[str]
    preview: str

@app.post("/generate-diagram", response_model=DiagramResponse)
async def generate_diagram(request: DiagramRequest):
    try:
        mermaid_code = generate_mermaid_code(request.diagram_type, request.prompt)
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            output_path = temp_file.name
        
        success = renderer.render_diagram(mermaid_code, output_path)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to render diagram")
        
        return DiagramResponse(
            mermaid_code=mermaid_code,
            image_path=output_path,
            preview=f"```mermaid\n{mermaid_code}\n```"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/diagram-types")
async def get_diagram_types():
    return [
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 