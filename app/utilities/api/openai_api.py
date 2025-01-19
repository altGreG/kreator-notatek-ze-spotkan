from openai import OpenAI
from loguru import logger as log

client = OpenAI()
try:
    completion = client.chat.completions.create(
        model="gpt-4o",
        store=True,
        messages=[
            {"role": "developer",
             "content": "You are a helpful assistant."},
            {"role": "user",
             "content": "write a haiku about ai"}
        ]
    )

    print(completion.choices[0].message)
except Exception as e:
    log.warning(f"Nie można wykonać zapytań API: {e}")