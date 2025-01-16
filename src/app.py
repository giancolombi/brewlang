from openai import OpenAI
import getpass
import os
from langchain_openai import ChatOpenAI



def main():
    print("Hello, World!")

    client = OpenAI(
    api_key="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"
    )

    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    store=True,
    messages=[
        {"role": "user", "content": "write a haiku about ai"}
    ]
    )

    print(completion.choices[0].message)

    if not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

    model = ChatOpenAI(model="gpt-4o-mini")
    model.invoke("Hello, world!")


if __name__ == "__main__":
    main()