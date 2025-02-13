import os
import datetime
import logging
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig, chain
from langchain_community.tools import TavilySearchResults

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()

# Define request model
class QueryRequest(BaseModel):
    user_input: str

# Define response model
class QueryResponse(BaseModel):
    response: str

# Load API Keys
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "your-openai-api-key"  # Set this in Docker

if not os.environ.get("TAVILY_API_KEY"):
    os.environ["TAVILY_API_KEY"] = "your-tavily-api-key"  # Set this in Docker

# Initialize LangChain Model
model = ChatOpenAI(model="gpt-4o-mini")
today = datetime.datetime.today().strftime("%D")

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", f"You are a helpful home coffee brewing assistant. The date today is {today}."),
        ("human", "{user_input}"),
        ("placeholder", "{messages}"),
    ]
)

tool = TavilySearchResults(
    max_results=5,
    search_depth="advanced",
    include_answer=True,
    include_raw_content=False,
    include_images=False,
)

# Bind tool to the model
llm_with_tools = model.bind_tools([tool])
llm_chain = prompt | llm_with_tools

@chain
async def tool_chain(user_input: str, config: RunnableConfig):
    logger.info(f"Processing user input: {user_input}")
    input_ = {"user_input": user_input}

    try:
        ai_msg = await llm_chain.ainvoke(input_, config=config)
        logger.info(f"AI model response: {ai_msg.content}")

        # If the tool was called, fetch results asynchronously
        if ai_msg.tool_calls:
            tool_msgs = await tool.abatch(ai_msg.tool_calls, config=config)
            logger.info(f"Tool responses: {[msg.content for msg in tool_msgs]}")
            return await llm_chain.ainvoke({**input_, "messages": [ai_msg, *tool_msgs]}, config=config)
        return ai_msg
    except Exception as e:
        logger.error(f"Error processing input: {e}", exc_info=True)
        raise e

@app.post("/query/", response_model=QueryResponse)
async def query_api(request: QueryRequest):
    logger.info(f"Received query: {request.user_input}")

    try:
        response = await tool_chain.ainvoke(request.user_input, config={})
        logger.info(f"Returning response: {response.content}")
        return QueryResponse(response=response.content)
    except Exception as e:
        logger.error(f"Error handling request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Serve static files
app.mount("/static", StaticFiles(directory="../static"), name="static")

@app.get("/")
async def serve_index():
    return RedirectResponse(url="/static/index.html")
