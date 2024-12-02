from tracet import Chain, ChatOllama


llm = ChatOllama(
    model="llama3.2:3b",
    streaming=True,
    max_tokens=64,
    temperature=0.9,
    repetition_penalty=1.2,
)

chain = Chain(
    "System: You are a helpful assistant.\n User: {input}",
    llm,
)


for token in chain.stream(input="What is python?"):
    print(token, end="", flush=True)

## Or, to register a system prompt correctly with a Chat model, we need to give it a list of messages

chain = Chain(llm)

for token in chain.stream(
    prompt="What is python?",
    messages=[{"role": "system", "content": "You are a helpful assistant."}],
):
    print(token, end="", flush=True)
