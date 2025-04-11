import os
import time
import openai
import gradio as gr

# API-Key und Assistant-ID sicher aus Hugging Face Secrets lesen
openai.api_key = os.getenv("OPENAI_API_KEY")
assistant_id = os.getenv("OPENAI_ASSISTANT_ID")

def frage_senden(user_message):
    try:
        # 1. Erstelle neuen Thread
        thread = openai.beta.threads.create()

        # 2. Füge die User-Nachricht zum Thread hinzu
        openai.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_message
        )

        # 3. Starte einen Run mit deinem Assistant
        run = openai.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id
        )

        # 4. Warte, bis der Run abgeschlossen ist
        while True:
            status = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if status.status == "completed":
                break
            elif status.status == "failed":
                return "⚠️ Die KI hat keine Antwort geliefert. Bitte nochmal versuchen."
            time.sleep(1)

        # 5. Hole die KI-Antwort
        messages = openai.beta.threads.messages.list(thread_id=thread.id)
        answer = messages.data[0].content[0].text.value
        return answer

    except Exception as e:
        return f"❌ Fehler: {str(e)}"

# Baue Gradio-Oberfläche
demo = gr.Interface(
    fn=frage_senden,
    inputs=gr.Textbox(label="📝 Deine Frage an den Lehrer-Buddy"),
    outputs=gr.Textbox(label="💡 Antwort von der KI"),
    title="📚 Lehrer-Buddy",
    description="Stell Fragen zu Schule, Lernen, Aufgaben – dein KI-Buddy hilft dir!"
)

demo.launch(server_name="0.0.0.0", server_port=7860)

print("🔍 Assistant-ID geladen:", assistant_id)
if assistant_id is None:
    raise ValueError("❌ Assistant-ID wurde nicht gefunden! Bitte prüfe das Hugging Face Secret.")

