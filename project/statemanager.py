# hormones: oxytocin, serotonin, cortisol, adrenaline and dopamine
# Decay rates: {oxy: 0.03 per cycle, serotonin: 0.05 per cycle, cortisol: 0.08% per cycle, adrenaline: 0.3% per cycle, dopamine: 0.15% per cycle}
# AI moods: Sad, happy, loving, caring, angry 

# - if intent caring while AI mood in [sad, happy, loving, caring] oxytocin up 
# - if intent loving while AI mood in [sad, happy, loving, caring] and oxytocin > 25%, oxytocin UP, serotonin UP (Because no one wants lovey stuff from someone they haven't bonded with much)
# - if intent happy while AI mood in [loving, caring], oxytocin up, serotonin up, dopamine up 
# - if intent sad while AI mood in [caring, loving], oxytocin up, cortisol slight up, serotonin slight down
# - if intent sad while AI mood angry, cortisol up, serotonin down
# - if intent sad while AI mood sad, serotonin down, oxytocin slight up 
# - if intent happy while AI mood sad, serotonin down, cortisol up
# - if intent angry while AI mood in [caring, loving], adrenaline up, serotonin slight down, cortisol up, oxytocin down
# if intent angry while AI mood angry, adrenaline up, cortisol up, serotonin down
# if intent angry while AI mood happy, serotonin down to below happiness level, adrenaline up, cortisol up 
# if intent loving while AI mood loving, dopamine up, oxytocin up, cortisol down, serotonin up 
# if intent thankful while AI mood in [caring, happy, loving] dopamine up, oxytocin up
# if intent sorry while AI mood angry and adrenaline < 65% and cortisol < 70%: cortisol down, oxytocin slight up, serotonin slight up
# if intent sorry while AI mood angry and not(adrenaline < 65% and cortisol < 70%): cortisol up, serotonin down, adrenaline slight down
# if intent thankful while AI mood angry cortisol up, serotonin down
# if intent thankful while AI mood sad, serotonin slight up
# if intent sorry while AI mood in [loving, caring, happy], oxytocin slight up if above 25%, serotonin slight up
# if intent sorry while AI mood sad, oxytocin up, serotonin up (depending on how low it is if almost 0 basically no increase if around 30 or so decent increase)
# if intent neutral while AI mood != neutral, apply decay rates only
# 

# Yes I used AI to write all of this boiler plate, I'm not writing all of these if statements by hand, bite me 
# Update AI couldn't implement it properly and sucked ass T-T I have to write all of this shit by hand T-T, I got bit 


class EmotionalStateManager:
    def __init__(self):
        """Initializes the AI's emotional state with baseline hormone levels."""
        self.hormones = {
            "oxytocin": 10.0, 
            "serotonin": 50.0,
            "cortisol": 20.0,
            "adrenaline": 5.0,
            "dopamine": 30.0
        }
        self.mood = ("neutral", 0) # tuple in the form of emotion, intensity

    def _apply_decay(self):
        self.hormones["oxytocin"] *= (1 - 0.08)
        self.hormones["serotonin"] *= (1 - 0.1)
        self.hormones["cortisol"] *= (1 - 0.13) 
        self.hormones["adrenaline"] *= (1 - 0.3)  
        self.hormones["dopamine"] *= (1 - 0.2)

    def _update_mood(self):
        if self.hormones["cortisol"] > 50 and self.hormones["serotonin"] < 40:
            self.mood = ("angry", (self.hormones["cortisol"] + self.hormones["adrenaline"])//2)
        elif self.hormones["serotonin"] < 40:
            self.mood = ("sad", ((100 - self.hormones["serotonin"]) + self.hormones["cortisol"])//2)
        elif self.hormones["oxytocin"] > 60 and self.hormones["serotonin"] > 55:
            self.mood = ("loving", (self.hormones["oxytocin"] + self.hormones["dopamine"] + self.hormones["serotonin"])//3)
        elif self.hormones["serotonin"] > 60:
            self.mood = ("happy", (self.hormones["dopamine"] + self.hormones["serotonin"])//2)
        elif self.hormones["oxytocin"] > 35:
            self.mood = ("caring", (self.hormones["oxytocin"] + self.hormones["serotonin"])//2)
        else:
            self.mood = ("neutral", 0)

    def _change_hormone(self, hormone, amount):
        self.hormones[hormone] = max(0, min(100, self.hormones[hormone] + amount))

    def update_state(self, user_intent):
        self._apply_decay()
        self.update_hormones(user_intent)
        self._update_mood()

    def display_state(self):
        """Prints the current state of the AI for debugging."""
        print(f"\n--- AI State Update ---")
        print(f"Current Mood: {self.mood[0].upper()}; Intensity: {self.mood[1]}")
        for hormone, value in self.hormones.items():
            print(f"  - {hormone.capitalize()}: {value:.2f}")
        print("-----------------------")
        
    def return_mood(self):
        return self.mood # tuple
        
    def update_hormones(self, user_intent):
        
        current_mood = self.mood[0]
        mood_intensity = self.mood[1]
        
        if user_intent == "user_caring":
            if current_mood in ["sad", "happy", "loving", "caring", "neutral"]:
                self._change_hormone("oxytocin", 15)
                self._change_hormone("dopamine", 25)
                self._change_hormone("serotonin", 15)
            elif current_mood == "angry":
                self._change_hormone("cortisol", 15)
                self._change_hormone("serotonin", -15)
                
        elif user_intent == "user_loving":
            if current_mood in ["sad", "happy", "caring", "neutral"]:
                if self.hormones["oxytocin"] > 25:
                    self._change_hormone("oxytocin", 15)
                    self._change_hormone("serotonin", 15)
                else:
                    self._change_hormone("serotonin", 15)
            elif current_mood == "loving": 
                self._change_hormone("dopamine", 25)
                self._change_hormone("oxytocin", 20)
                self._change_hormone("cortisol", -15)
                self._change_hormone("serotonin", 20)
            elif current_mood == "angry":
                self._change_hormone("cortisol", 20)
                self._change_hormone("adrenaline", 25)

        elif user_intent == "user_feeling_bad": 
            if current_mood in ["caring", "loving"]:
                self._change_hormone("cortisol", 10)
                self._change_hormone("oxytocin", 20)
                self._change_hormone("serotonin", -10)
            elif current_mood == "angry":
                self._change_hormone("cortisol", 20)
                self._change_hormone("serotonin", -20)
            elif current_mood in ["neutral", "sad"]:
                self._change_hormone("oxytocin", 10)
                self._change_hormone("serotonin", -15)
            else: # happy
                self._change_hormone("serotonin", -15)
            
        elif user_intent == "user_happy":
            if current_mood in ["caring", "loving", "happy"]:
                self._change_hormone("cortisol", -5)
                self._change_hormone("oxytocin", 20)
                self._change_hormone("serotonin", 20)
                self._change_hormone("dopamine", 25)
            elif current_mood in ["sad", "angry"]:
                self._change_hormone("cortisol", 15)
                self._change_hormone("serotonin", -15)
            else: # neutral
                self._change_hormone("serotonin", 15)
                self._change_hormone("dopamine", 15)
                
        elif user_intent == "user_angry":
            if current_mood in ["caring", "loving"]:
                self._change_hormone("cortisol", 20)
                self._change_hormone("adrenaline", 40)
                self._change_hormone("oxytocin", -15)
                self.hormones["serotonin"] = 35 
            elif current_mood == "angry":
                self._change_hormone("cortisol", 20)
                self._change_hormone("adrenaline", 40)
                self._change_hormone("serotonin", -25) 
            elif current_mood == "happy": 
                self._change_hormone("cortisol", 20)
                self._change_hormone("adrenaline", 40)
                self.hormones["serotonin"] = 35
            else: # sad and neutral
                self._change_hormone("cortisol", 15)
                self._change_hormone("adrenaline", 25)
                self._change_hormone("serotonin", -15)

        elif user_intent == "user_thankful":
            if current_mood in ["caring", "happy", "loving"]:
                self._change_hormone("dopamine", 20)
                self._change_hormone("serotonin", 25)
                self._change_hormone("oxytocin", 20)
            elif current_mood == "angry":
                self._change_hormone("cortisol", 15)
                self._change_hormone("serotonin", -15)
            elif current_mood == "sad":
                self._change_hormone("serotonin", 10)
            else: # neutral 
                self._change_hormone("dopamine", 10)
                self._change_hormone("serotonin", 5)
                self._change_hormone("oxytocin", 10)

        elif user_intent == "user_sorry":
            if current_mood == "angry":
                if mood_intensity < 65:
                    self._change_hormone("cortisol", -20)
                    self._change_hormone("oxytocin", 10)
                    self._change_hormone("serotonin", 10)
                else: 
                    self._change_hormone("cortisol", 15)
                    self._change_hormone("serotonin", -15)
                    self._change_hormone("adrenaline", -10)
            elif current_mood in ["loving", "caring", "happy", "neutral"]:
                if self.hormones["oxytocin"] > 25:
                    self._change_hormone("oxytocin", 10)
                self._change_hormone("serotonin", 10)
                self._change_hormone("dopamine", 15)
            elif current_mood == "sad":
                self._change_hormone("oxytocin", 15)
                # Implements: "if almost 0 no increase, if around 30 decent increase"
                serotonin_increase = 15 * (self.hormones["serotonin"] / 30)
                self._change_hormone("serotonin", max(0, serotonin_increase))
        
        elif user_intent == "neutral":
            if current_mood == "angry":
                self._change_hormone("cortisol", -5) 
                self._change_hormone("adrenaline", -10) 
                self._change_hormone("serotonin", -5) 
            elif current_mood == "sad":
                self._change_hormone("oxytocin", -5)
                self._change_hormone("serotonin", -5)
            elif current_mood in ["happy", "loving", "caring"]:
                self._change_hormone("dopamine", -5)
                self._change_hormone("oxytocin", -5 if current_mood != "happy" else 0)
                self._change_hormone("serotonin", -5)
            # no else because if neutral on neutral i just need to apply decay

# --- Example Usage ---
if __name__ == "__main__":
    ai_state = EmotionalStateManager()
    print("--- Initial State ---")
    ai_state.display_state()

    # Simulate a conversation
    print("\n>>> User: 'Hey, how are you holding up?'")
    ai_state.update_state(user_intent="user_caring") # Mood should become 'caring'
    ai_state.display_state()

    print("\n>>> User: 'You're the best, I love you!'")
    ai_state.update_state(user_intent="user_loving") # Mood should become 'loving'
    ai_state.display_state()

    print("\n>>> User: 'This is bullshit, you're an idiot!'")
    ai_state.update_state(user_intent="user_angry") # Mood should become 'angry'
    ai_state.display_state()
    
    print("\n>>> User: 'I'm sorry, I was out of line.'")
    ai_state.update_state(user_intent="user_sorry") # Apology quells anger
    ai_state.display_state()
    
    print("\n>>> User: 'What's the weather like?'")
    ai_state.update_state(user_intent="neutral") # Should decay
    ai_state.display_state()
    
    print("\n>>> User: 'Seriously, my apologies.'")
    ai_state.update_state(user_intent="user_sorry") # AI gets a slight serotonin boost due to the apology even though it doesn't feel sad about it anymore
    ai_state.display_state()