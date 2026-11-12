"""
SupeRR Selector — Web Application Entrypoint
Elite Cricket Pressure Intelligence Platform

Launches the FastAPI backend and serves the interactive frontend application.
Access locally at: http://localhost:8000
"""

import sys
import uvicorn
from src.config import PROJECT_ROOT

def main():
    print("=" * 70)
    print("SupeRR Selector Season 2 — Elite Cricket Pressure Intelligence Platform")
    print("=" * 70)
    print(f"Project Root: {PROJECT_ROOT}")
    print("Starting Uvicorn server on http://localhost:8000 ...")
    print("Direct all browser navigation to: http://localhost:8000")
    print("Press CTRL+C to stop the server.")
    print("=" * 70)
    
    uvicorn.run(
        "src.api:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()
