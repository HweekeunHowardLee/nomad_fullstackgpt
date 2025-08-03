from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

def get_weather(city):
    # This function would normally call a weather API to get the weather for the city
    return f"The weather in {city} is sunny with a high of 25°C."

function = {
    "name": "get_weather",
    "description": "Get the current weather for a given city.",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "The name of the city to get the weather for.",
            },
        },
        "required": ["city"],
    }
}


llm = ChatOpenAI(
    temperature=0.1,
).bind(
    function_call={"auto": True},
    functions=[
        function,
    ],
)

prompt = PromptTemplate.from_template("What's the weather like in {city}")

chain = prompt | llm

response = chain.invoke({"city": "rome"})

response.content