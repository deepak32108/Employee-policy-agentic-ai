from src.utils.llm import get_llm

llm = get_llm()

response = llm.invoke("Hello")

print(response.content)
