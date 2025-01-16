from openai import OpenAI
import getpass
import os
from langchain_openai import ChatOpenAI



def main():
    print("Hello, World!")

    if not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

    model = ChatOpenAI(model="gpt-4o-mini")
    model.invoke("Hello, world!")


if __name__ == "__main__":
    main()