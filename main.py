from openai import OpenAI
import openai
import os
import time
import json
from dotenv import load_dotenv

 # Criação do cliente OpenAI dentro da função main
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def wait_on_run(run_id, thread_id):
    run = client.beta.threads.runs.retrieve(
        thread_id=thread_id,
        run_id=run_id,
    )
    print("Status inicial do Run:", run.status)
    
    while run.status == "queued" or run.status == "in_progress":
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id,
        )
        time.sleep(0.5)
        print("Status atual  tentativa 2 do Run:", run.status)
    print("Status final do Run:", run.status)    
    return run
def show_json(obj):
    print(json.loads(obj.model_dump_json()))
    
def process_run_response(run_id, thread_id):
    # Aguarda a conclusão do run
    run = wait_on_run(run_id, thread_id)

    # Verifica se o run foi concluído com sucesso
    if run.status == 'completed':
        # Recupera a resposta do run
        response = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )

        # Processa a resposta (aqui você pode adicionar sua lógica específica)
        # Por exemplo, imprimindo a resposta
        print("Resposta do Run:", response.model_dump_json())

        # Retornar a resposta ou o processamento dela
        return response
    else:
        print("Run não foi concluído com sucesso.")
        return None
    
def main():
    load_dotenv()

   

    # Definindo as funções fictícias no assistente
    assistant = client.beta.assistants.create(
        name="Example Assistant",
        instructions="You are an assistant. Answer questions using your knowledge base.",
        model="gpt-3.5-turbo",
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
    
    show_json(assistant)

    thread = client.beta.threads.create()
    show_json(thread)
    
    # Enviando uma mensagem para iniciar a interação
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="I need to solve the equation `3x + 11 = 14`. Can you help me?"
    )
    show_json(message)

    message_content = ''.join([item.text.value for item in message.content if hasattr(item, 'text')])
    # Criando o 'run'
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions=f"Answer the user's question: {message_content}"

    )
    
    show_json(run)
    
    process_run_response(run.id, thread.id)

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    show_json(messages)
    
    process_run_response(run.id, thread.id)


if __name__ == "__main__":
    main()
