import ollama
import requests
import json

OLLAMA_HOST = 'http://localhost:11434'

# generate response from ollama language model
def generate(model: str, system: str, prompt: str, template: str = None, context: str = None, options: str = None, callback: bool = None):
    # ollama.generate(model=model, prompt=prompt)
    # final_result = ""
    # api: /api/generate -> model, prompt, system

    try:
        url = f"{OLLAMA_HOST}/api/generate"
        payload = {
            "model": model, 
            "prompt": prompt, 
            "system": system, 
            "template": template, 
            "context": context, 
            "options": options
        }
        
        # Remove keys with None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        with requests.post(url, json=payload, stream=True) as response:
            response.raise_for_status()
            
            final_context = None
            full_response = ""

            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    
                    if callback:
                        callback(chunk)
                    else:
                        if not chunk.get("done"):
                            response_piece = chunk.get("response", "")
                            full_response += response_piece
                            # print(response_piece, end="", flush=True)
                    
                    if chunk.get("done"):
                        final_context = chunk.get("context")
            
            return full_response, final_context
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None, None