Write-Host "Make sure Ollama is running (ollama serve) before starting the backend."

try {
    Start-Process ollama -ArgumentList "serve" -NoNewWindow -ErrorAction SilentlyContinue | Out-Null
} catch {
    Write-Host "Ollama was not started by this script. It may already be running or unavailable on PATH."
}

python -m pip install fastapi uvicorn jsonschema requests

uvicorn main:app --reload --port 8000
