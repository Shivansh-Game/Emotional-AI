import torch
from pps import preprocess, tokenize
from model import IntentClassifier
from statemanager import EmotionalStateManager
from llm import LLMChatbot

def model_components():
    device = "cuda" if torch.cuda.is_available() else "cpu" # irrelavant for me personally since I don't have a gpu but enables y'all to use GPUs if you have em

    # load model data
    FILE = "trained_data.pth"
    data = torch.load(FILE)

    # seperate the variablessssssss
    vocab_size = data["vocab_size"]
    embedding_dim = data["embedding_dim"]
    hidden_size = data["hidden_size"]
    num_tags = data["num_tags"]
    model_state = data["model_state"]
    vocabulary = data["vocabulary"]
    tags = data["tags"]

    # --- RECREATE THE MODEL --- #
    model = IntentClassifier(vocab_size, embedding_dim, hidden_size, num_tags).to(device)
    # Load the saved weightssss
    model.load_state_dict(model_state)

    model.eval()
    
    return tags, vocabulary, model, device



def preprocess_sentence(sentence, vocabulary, device):
    tokens = tokenize(sentence)
    processed_words = [preprocess(token) for token in tokens]
    print(processed_words)
    indices = []
    
    ignore_words = ['?', '.', '!']
    
    
    for w in processed_words:
        if w in vocabulary:
            indices.append(vocabulary.index(w))
        elif w in ignore_words:
            pass
        else:
            indices.append(vocabulary.index("<UNK>"))

    if not indices:
        return None
    
    return torch.tensor(indices).view(1, -1).to(device)

def make_prediction(input_tensor, BOT_NAME, model, tags):
    if input_tensor is None:
        return f"{BOT_NAME}: Sorry, I don't know any of those words."
    # torch.no_grad() is used to improve performance (Inference)
    with torch.no_grad():
        output = model(input_tensor)
    probabilities = torch.softmax(output, dim=1)
    max_prob, predicted_idx = torch.max(probabilities, dim=1)
    predicted_tag = tags[predicted_idx.item()]
    return max_prob, predicted_tag

if __name__ == '__main__':
    
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

    print(f"\n--- {chatbot.ai_name} Ready --- (Type 'quit' to exit)")
    while True:
        user_sentence = input("You: ")
        if user_sentence.lower() == "quit":
            break
        if not user_sentence.strip():
            continue
        
        input_tensor = preprocess_sentence(user_sentence, vocabulary, device)

        confidence, predicted_tag = make_prediction(input_tensor, "intent_guesser", model, tags)

        print(float(confidence))
        print(predicted_tag)

        if float(confidence) < 0.7:
            print("passed")
            statemanager._apply_decay()
        else:
            statemanager.update_state(predicted_tag)
            statemanager.display_state()

        current_mood_str, current_intensity_int = statemanager.return_mood()

        # using streaming now 

        print(f"{chatbot.ai_name}: ", end="", flush=True)
        try:
            for chunk in chatbot.generate_response(user_sentence, current_mood_str, current_intensity_int):
                print(chunk, end="", flush=True)
            print()
        except Exception as e:
            print(f"\nError during response generation: {e}")
            print()