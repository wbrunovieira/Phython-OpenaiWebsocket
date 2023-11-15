from openai import OpenAI
import openai
import os
import time
import json
from dotenv import load_dotenv

def main():
    load_dotenv()

    # Criação do cliente OpenAI dentro da função main
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Definindo as funções fictícias no assistente
    assistant = client.beta.assistants.create(
        name="Example Assistant",
        instructions="You are an assistant. Answer questions using your knowledge base.",
        model="gpt-3.5-turbo-1106",
        tools=[{
            "type": "function",
            "function": {
                "name": "exampleFunction",
                "description": "Example function description",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "param1": {"type": "string", "description": "Example parameter"}
                    },
                    "required": ["param1"]
                }
            }
        }]
    )

    thread = client.beta.threads.create()

    # Enviando uma mensagem para iniciar a interação
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="Please provide an example response."
    )

    # Criando o 'run'
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions="Answer the user's question."
    )

    timeout = 60  # segundos
    start_time = time.time()

    while True:
        current_run = client.beta.threads.runs.retrieve(run_id=run.id, thread_id=thread.id)

        if current_run.status == 'requires_action':
            # Processar as funções chamadas aqui
            # ...

        if current_run.status == 'completed':
            print("Run completed!")
            break

        if time.time() - start_time > timeout:
            print("Timeout reached, resending the request.")
            # ...

        time.sleep(5)

    # Recuperar e imprimir todas as mensagens da thread
    # ...

if __name__ == "__main__":
    main()
