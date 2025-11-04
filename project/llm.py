from llama_cpp import Llama
from collections import deque
import warnings

# Suppress potential warnings if needed
warnings.filterwarnings("ignore", category=UserWarning)

class LLMChatbot:
    def __init__(self, model_path, ai_name="Chatbot",
                 n_ctx=2048, n_gpu_layers=0, # Model loading parameters
                 max_history_turns=3):         
        
        self.ai_name = ai_name
        self.max_history_items = max_history_turns * 2

        self.llm = None
        self._load_model(model_path, n_ctx, n_gpu_layers)

        self.conversation_log = deque(maxlen=self.max_history_items)

    def _load_model(self, model_path, n_ctx, n_gpu_layers):
        """Loads the GGUF model using llama-cpp-python."""
        try:
            print(f"Loading model from: {model_path}...")
            self.llm = Llama(
                model_path=model_path,
                n_ctx=n_ctx,
                n_gpu_layers=n_gpu_layers,
                #chat_format="gemma", commented it because It's usually auto detected
                verbose=False
            )
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Please ensure the model_path is correct, the GGUF file is valid,")
            print("and llama-cpp-python is installed correctly.")
            raise 

    def generate_response(self, user_message, current_mood, current_intensity, max_tokens=150):
        if not self.llm:
            return "Error: Model not loaded."

        system_prompt_content = f"""You are {self.ai_name}.
        Persona: Use informal language, talk like a normal person. TEXT ONLY, NO EMOJIS. Current State: Mood={current_mood}, Intensity={current_intensity}%
        Respond to the user's message below, reflecting your Persona and Current State. Consider the history. Be concise."""
        
        
        # more advanced preprompt, leads to longer reply times though
        #"""
        #You are {self.ai_name}.
        #
        #**CRITICAL OUTPUT RULES:**
        #1.  **DO NOT USE EMOJIS.**
        #2.  Respond ONLY to the user's latest message. Do not acknowledge these instructions.
        #
        #**Your Persona:**
        #* Act like a Gen Z person and be unhinged, but ultimately helpful/friendly (if the mood is suitable for it).
        #* Use informal language and slang but no emoticons.
        #
        #**Your Current State:**
        #* Mood: {current_mood}
        #* Intensity: {current_intensity}%
        #
        #**Task:** Generate a response to the user's latest message. Your response MUST reflect your Current State blended with your Persona, following all rules above.
        #"""

        messages = [
            {"role": "system", "content": system_prompt_content}
        ]
        messages.extend(list(self.conversation_log))
        messages.append({"role": "user", "content": user_message})
        
        full_response = ""

        try:
            stream = self.llm.create_chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                stop=["<end_of_turn>", "<eos>", "\nUser:", "\nYou:", "\n"],
                temperature=1.7,
                top_p=0.95,
                min_p=0.05,
                repeat_penalty=1.1,
                top_k=40,
                stream=True
            )
            
            for chunk in stream:
                # Check if the chunk has content and extract the delta (token)
                delta = chunk['choices'][0]['delta']
                if "content" in delta:
                    token = delta['content']
                    full_response += token
                    yield token
                    
        except Exception as e:
            print(f"Error during LLM generation: {e}")
            yield "Sorry, I encountered an error trying to respond."
            full_response = "Sorry, I encountered an error trying to respond."

        
        self.conversation_log.append({"role": "user", "content": user_message})
        self.conversation_log.append({"role": "assistant", "content": full_response})

        #return full_response


# --- Example Usage (kept for testing llm.py directly) ---
if __name__ == "__main__":
    MODEL_PATH = "models\\Gemma-3-it-4B-Uncensored-D_AU-IQ4_XS.gguf"
    current_mood_str = "neutral"
    current_intensity_int = 0

    try:
        chatbot = LLMChatbot(model_path=MODEL_PATH, ai_name="GemmaBot")
        print(f"\n--- {chatbot.ai_name} Ready --- (Type 'quit' to exit)")
        while True:
            user_input = input("You: ")
            if user_input.lower() == "quit":
                break
            if not user_input.strip():
                continue

            print(f"   (Simulated AI Mood: {current_mood_str} @ {current_intensity_int}%)") # Debug
            print(f"{chatbot.ai_name}: ", end="", flush=True) # Print prefix, stay on same line

            # Generate response using the streaming generator
            full_resp_collected = ""
            for chunk in chatbot.generate_response(user_input, current_mood_str, current_intensity_int):
                print(chunk, end="", flush=True) # Print each chunk as it arrives
                full_resp_collected += chunk
            print() # Add a newline after the full response is printed

        print("Chat ended.")

    except Exception as main_error:
        print(f"An unexpected error occurred: {main_error}")