from websocket import create_connection

ws = create_connection("ws://localhost:8000/ws")
ws.send("Olá, WebSocket!")
response = ws.recv()
print("Received:", response)
ws.close()
