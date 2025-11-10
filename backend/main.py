from fastapi import FastAPI, Request
from model.load_model import model_pipelines
from fastapi.middleware.cors import CORSMiddleware

#debugging
print("Loaded models:", list(model_pipelines.keys()))

app = FastAPI(title="Fine-Tuned Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for testing, or specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Chatbot API is running on RunPod!"}

@app.post("/chat/{model_name}")
async def chat(model_name: str, request: Request):
    if model_name not in model_pipelines:
        return {"error": "Model not found"}

    data = await request.json()
    prompt = data.get("message", "")

    response = model_pipelines[model_name](
        prompt,
        max_new_tokens=200,
        temperature=0.7,
        top_p=0.9
    )[0]["generated_text"].replace(prompt, "").strip()

    response_text = response

    # Remove instruction markup
    if "### Response:" in response:
        response_text = response.split("### Response:")[-1].strip()

    return {"response": response_text}


