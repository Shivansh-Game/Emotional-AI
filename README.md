# Stateful Emotional AI (Project: "Emotional NPC")

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0-red?logo=pytorch&logoColor=white)
![llama-cpp-python](https://img.shields.io/badge/llama--cpp-gray?logo=c%2B%2B&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-green?logo=pytest&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-purple)

A multi-component system that simulates a stateful, dynamic, and "flawed" AI personality. The AI's responses are not stateless reactions to a user's prompt; they are dictated by its own internal "emotional state," which is managed by a "hormone-based" logic engine and powered by a local, streaming LLM.

## Core Architecture

I architected this system in three distinct, decoupled stages:

### 1. The "Ears": The Emotion Classifier
This component's job is to *perceive* the user's emotional intent.

* This system is built on top of my [**Gen Z Emotion Classifier**]([https://github.com/Shivansh-Game/Gen-z-Emotional-Intent-Classifier]) project, a `pytest`-validated model with **~94% accuracy.**
* **Architecture:** It's a custom PyTorch model featuring an `nn.Embedding` layer and a custom-built **Attention Pooling** mechanism to create context-aware sentence vectors.
* **Data:** It was trained on my own `Unk_infested_intents.json` dataset, which I curated to handle nuanced, sarcastic, and elongated "Gen Z" lingo (`damnnn` is a different token from `damn`) and uses a `<UNK>` token for robustness.

### 2. The "Brain": The State Manager
This component's job is to *feel*. It is a complex, stateful logic engine that simulates a dynamic personality.

* **Architecture:** A "Hormone-Based" state machine that tracks and decays five "hormones" (e.g., `Cortisol`, `Oxytocin`, `Dopamine`).
* **Dynamic Logic:** The classifier's intent (from Stage 1) and the AI's current "mood" are fed into a rule engine. This creates believable, non-deterministic behavior.
* **Example Rule:** An `intent_sorry` from the user will *increase* `Cortisol` (annoyance) if the AI's `current_mood` is already `angry`, but will *increase* `Oxytocin` (bonding) if the `current_mood` is `caring`.

### 3. The "Mouth": The LLM
This component's job is to *express* the AI's current mood.

* **Architecture:** An uncensored **Gemma 3 (4-bit GGUF)** model running locally via `llama-cpp-python`.
* **Dynamic Preprompting:** The "mood" and "intensity" from the Brain are used to **dynamically generate a new system preprompt for *every single response*.** This is what changes the AI's personality from "caring" to "angry" in real-time.
* **Optimization:** The model uses **streaming inference** to provide a "live typing" effect, creating a responsive user experience by solving the 15-20 second "think time" bottleneck.

## Tech Stack
* **PyTorch:** For the Deep Learning classifier.
* **`llama-cpp-python`:** For efficient, local LLM inference.
* **NLTK:** For the NLP preprocessing pipeline (lemmatization).
* **`pytest`:** For validation and fine-tuning the classifier.


## Future Goals (My Next "Sprint")
This project is the foundation for a larger goal. My current focus is on closing the "pro-level" MLOps gap. My next "Sprint" is to:
1.  **Containerize** this entire application with **Docker**.
2.  **Deploy** it as a scalable, on-demand, serverless API on **AWS**.
