import os
import gradio as gr
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from dotenv import load_dotenv
from system_prompt import system_prompt, suggested_questions

load_dotenv()

openai_api_key= os.getenv("OPENAI_API_KEY")

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

llm = ChatOpenAI(
    model = "gpt-4",
    openai_api_key = openai_api_key,
    temperature=0.7
)

chain = prompt | llm

#memory function
store = {}
def get_memory(session_id):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

chat_with_memory = RunnableWithMessageHistory(
    chain,
    get_memory,
    input_messages_key="input",
    history_messages_key="history"
)

#function for memory summary if user ask
MEMORY_TRIGGERS = [
    "what did i say", "what did i tell", "do you remember",
    "what have we talked", "our chat", "conversation summary",
    "recap", "remember what i asked", "summarize our chat"
]

def is_memory_request(text):
    text = text.lower()
    return any(trigger in text for trigger in MEMORY_TRIGGERS)

#function to generate personalized plan
def generate_meal_plan(age, weight, diet_preference):
    diet_preference = diet_preference.lower()

    if diet_preference == "Weight loss":
        meal_plan = f"Breakfast: Oatmeal with berries and almond butter\nLunch: Grilled chicken salad\nDinner: Baked salmon with steamed veggies\nSnack: Greek yogurt with chia seeds"
    elif diet_preference == "Muscle gain":
        meal_plan = f"Breakfast: Scrambled eggs with avocado and whole grain toast\nLunch: Grilled chicken with quinoa and broccoli\nDinner: Beef stir-fry with brown rice\nSnack: Protein smoothie with banana"
    elif diet_preference == "Vegetarian":
        meal_plan = f"Breakfast: Chia pudding with almond milk and berries\nLunch: Lentil soup with whole wheat bread\nDinner: Quinoa salad with roasted vegetables\nSnack: Hummus with carrot sticks"
    elif diet_preference == "Keto":
        meal_plan = f"Breakfast: Scrambled eggs with spinach and avocado\nLunch: Chicken salad with olive oil dressing\nDinner: Grilled steak with steamed cauliflower\nSnack: Cheese and nuts"
    elif diet_preference == "Diabetic":
        meal_plan = f"Breakfast: Steel-cut oats with chia seeds\nLunch: Grilled chicken with steamed vegetables\nDinner: Baked salmon with roasted sweet potatoes\nSnack: Almonds and a small apple"
    else:
        meal_plan = "Sorry, I couldn't generate a meal plan based on that diet preference."

    return meal_plan


#gradio chat handler function
def chat_fn(user_input, suggestion_input, state):
    session_id = "nutri-session"

    # initialize state if empty
    if state is None:
        state = {"history": [], "user_info": {}}

    history = state.get("history", [])
    user_info = state.get("user_info", {})
    state.update({"history": history, "user_info": user_info})

    # if user select suggestion question
    if not user_input and suggestion_input:
        user_input = suggestion_input
        suggestion_input = None
    elif not user_input:
        return state.get("history", []), state, None, ""

    # meal plan logic
    if "meal plan" in user_input.lower():
        missing_fields = []
        if "age" not in user_info:
            missing_fields.append("age")
        if "weight" not in user_info:
            missing_fields.append("weight")
        if "dietary preference" not in user_info:
            missing_fields.append("dietary preference")

        if missing_fields:
            next_field = missing_fields[0]
            user_info["expecting"] = next_field

            if next_field == "age":
                response = "To create your meal plan, I need to know your age. How old are you?"
            elif next_field == "weight":
                response = "Thanks! Next, what’s your weight in kilograms?"
            elif next_field == "dietary preference":
                response = "Great! Lastly, what’s your dietary preference? (e.g., Weight loss, Muscle gain, Vegetarian, Keto, Diabetic)"

            history.append((user_input, response))
            state.update({"history": history, "user_info": user_info})
            return history, state, None, ""

    elif all(k in user_info for k in ["age", "weight", "dietary preference"]) and any(
        phrase in user_input.lower() for phrase in ["generate", "yes", "ok", "sure", "plan", "show me", "meal"]
    ):
        meal_plan = generate_meal_plan(
            user_info['age'], user_info['weight'], user_info['dietary preference']
        )
        response = f"Here’s your personalized meal plan based on your goals:\n\n{meal_plan}"
        history.append((user_input, response))
        state.update({"history": history, "user_info": user_info})
        return history, state, None, ""

    # collect user info
    if user_info.get("expecting") == "age":
        user_info["age"] = user_input
        user_info["expecting"] = "weight"
        response = "Got it! What's your weight?"
        history.append((user_input, response))
        state.update({"history": history, "user_info": user_info})
        return history, state, None, ""

    elif user_info.get("expecting") == "weight":
        user_info["weight"] = user_input
        user_info["expecting"] = "dietary preference"
        response = "Got it! What’s your dietary preference? (e.g., Weight loss, Muscle gain, Vegetarian, Keto, Diabetic)"
        history.append((user_input, response))
        state.update({"history": history, "user_info": user_info})
        return history, state, None, ""

    elif user_info.get("expecting") == "dietary preference":
        user_info["dietary preference"] = user_input
        user_info.pop("expecting", None)  
        response = "Thanks! I have all the information I need. Would you like me to generate a meal plan for you?"
        history.append((user_input, response))
        state.update({"history": history, "user_info": user_info})
        return history, state, None, ""

    # User asks for memory
    if is_memory_request(user_input):
        memory = get_memory(session_id)
        messages = memory.messages

        if not messages:
            response = "We haven’t really talked yet — ask me something about nutrition!"
        else:
            summary = "\n".join([f"{msg.type.title()}: {msg.content}" for msg in messages[-6:]])
            response = f"Here’s a quick summary of our recent chat:\n\n{summary}"

        history.append((user_input, response))
        state.update({"history": history, "user_info": user_info})
        return history, state, None, ""

    result = chat_with_memory.invoke(
        {"input": user_input},
        config={"configurable": {"session_id": session_id}}
    )
    history.append((user_input, result.content))
    state.update({"history": history, "user_info": user_info})
    return history, state, None, ""

# UI interface for front-end
with gr.Blocks(css="""
    #chatbot {
        height: 400px;
        overflow-y: auto;
    }

    .suggestion-button label {
        background-color: #f0f4f8 !important; /* light gray-blue */
        color: #1a1a1a !important;            /* dark text for contrast */
        border-radius: 12px;
        padding: 8px 14px;
        cursor: pointer;
        margin: 4px;
        border: 1px solid #d0d7de;
        transition: all 0.2s ease-in-out;
        font-weight: 500;
    }

    .suggestion-button label:hover {
        background-color: #d9e9f7 !important; /* subtle blue on hover */
        color: #000000 !important;
    }
""") as interface:
    gr.HTML("<script>document.title = 'NAVI — AI Nutrition Assistant';</script>")

    gr.Markdown("🌿 NAVI — AI Nutrition Assistant")
    gr.Markdown("I'm your nutrition assistant — ask anything about healthy eating or meal plans, or choose a question below to begin!")

    with gr.Row():
        chatbot = gr.Chatbot(elem_id="chatbot", label="Chat with NAVI")

    with gr.Row():
        user_input_box = gr.Textbox(
            placeholder="Type your question here...",
            show_label=False,
            lines=1,
            scale=6
        )

    with gr.Row():
        suggestion_input = gr.Radio(
            choices=suggested_questions,
            label="💡 Suggested Questions",
            interactive=True,
            elem_classes="suggestion-button",
            value= None
        )

    state = gr.State({"history": [], "user_info": {}})

    user_input_box.submit(
        chat_fn,
        inputs=[user_input_box, suggestion_input, state],
        outputs=[chatbot, state, suggestion_input, user_input_box]
    )

    suggestion_input.change(
        chat_fn,
        inputs=[suggestion_input, suggestion_input, state],
        outputs=[chatbot, state, suggestion_input, user_input_box]
    )

if __name__ == "__main__":
    interface.launch()