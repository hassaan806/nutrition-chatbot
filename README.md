# NAVI — AI Nutrition Assistant 🌿

**NAVI** is an AI-powered chatbot that provides personalized nutrition advice and meal plans tailored to user needs. Whether you're looking to lose weight, build muscle, or follow a specific diet like vegetarian or keto, NAVI helps guide your nutrition journey through engaging and intelligent conversation.

## 🧠 Features

- **Personalized Meal Plans** — Generated based on age, weight, and dietary goals.
- **Natural Chat Interface** — Ask questions about healthy eating or start with suggested prompts.
- **Interactive Memory** — Remembers previous inputs and offers summaries upon request.
- **Clean UI with Suggestions** — Intuitive design powered by Gradio for a smooth user experience.

## 💡 Example Diet Preferences Supported

- Weight loss
- Muscle gain
- Vegetarian
- Keto
- Diabetic

## ✨ How It Works

Users engage with NAVI via a chat interface. The assistant collects basic health info and dietary goals, then generates a personalized meal plan. It uses memory to maintain context across sessions and can summarize recent conversations when asked.

## 🚀 Live Demo

> Check out the deployed chatbot on [Hugging Face Spaces](https://huggingface.co/spaces/hassaan806/nutrition-chatbot) *(example link — replace with your actual URL if different)*

## 📁 Project Structure

nutrition-chatbot/ ├── main.py # Main Gradio app ├── system_prompt.py # System message and suggested questions ├── requirements.txt # Project dependencies ├── .env # Environment variables (not pushed to repo)


## 📜 License

This project is open-source and available under the MIT License.

## 🙏 Acknowledgments

- [OpenAI](https://openai.com/) — GPT-4 model for response generation.
- [LangChain](https://www.langchain.com/) — For message history and chaining prompts.
- [Gradio](https://gradio.app/) — For the web interface.
