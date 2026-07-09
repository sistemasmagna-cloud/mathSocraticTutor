from google import genai

client = genai.Client(api_key="chave")

# Lista todos os modelos que sua chave tem permissão para usar
print("Modelos disponíveis para esta chave:")
for m in client.models.list():
    print(f"- {m.name}")