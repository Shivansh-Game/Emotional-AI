# Hey retard when dockerising this remove the useless stuff in the folder

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from chat import make_prediction, preprocess_sentence, model_components
from statemanager import EmotionalStateManager
from llm import LLMChatbot
import asyncio

# port must be 8000 for the program to run
# run By running this python file and then enter uvicorn backend:app --port 8000 --reload in the terminal

# initializing app
app = FastAPI()

# initializing things for the model itself
tags, vocabulary, model, device = model_components()
statemanager = EmotionalStateManager()
path = "models\\Gemma-3-it-4B-Uncensored-D_AU-IQ4_XS.gguf"
current_mood_str = "neutral"
current_intensity_int = 0
name = "Emotional AI"
try:
    chatbot = LLMChatbot(model_path=path, ai_name=name)
except Exception as e:
    print(f"Failed to initialize chatbot: {e}")
    exit()


# allows communication between frontend and backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# lets it know we're expecting an input in the format of {'message' : str}
class ChatRequest(BaseModel):
    message: str 
    
async def stream_llm_response(user_message: str, mood: str, intensity: int):
    try:
        for chunk in chatbot.generate_response(user_message, mood, intensity):
            yield chunk # send chunk to the client
            await asyncio.sleep(0.01) # small sleep to prevent blocking event loop excessively if generation is very fast
    except Exception as e:
        print(f"\nError during streaming response generation: {e}")
        yield f"Error: Could not generate response. {e}" # send error message back


@app.post("/chat")
async def chat(request: ChatRequest): 
    user_message = request.message.strip()

    input_tensor = preprocess_sentence(user_message, vocabulary, device)

    if input_tensor is None:
         async def error_stream():
             yield "Error: Cannot process input with known words."
         return StreamingResponse(error_stream(), media_type="text/plain")


    confidence_tensor, predicted_tag = make_prediction(input_tensor, "intent_guesser", model, tags)
    confidence = float(confidence_tensor.item())

    print(f"{confidence=:.4f}, {predicted_tag=}")

    intent_to_use = predicted_tag
    if confidence < 0.7:
        print("Low confidence - applying decay only")
        statemanager._apply_decay()
        statemanager._update_mood()
    else:
        statemanager.update_state(predicted_tag)
        statemanager.display_state()

    current_mood_str, current_intensity_int = statemanager.return_mood()
    print(f"   (Current AI Mood: {current_mood_str} @ {current_intensity_int}%)")

    return StreamingResponse(
        stream_llm_response(user_message, current_mood_str, current_intensity_int),
        media_type="text/plain"
    )