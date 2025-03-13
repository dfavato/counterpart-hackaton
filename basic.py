from typing import Annotated

from langchain_core.tools import Tool
from langchain_google_community import GoogleSearchAPIWrapper
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict
from langgraph.checkpoint.memory import MemorySaver


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


llm = ChatOpenAI()
google_search = GoogleSearchAPIWrapper()


def top10_results(query: str):
    return google_search.results(query, 10)


google_search_results = Tool(
    name="google_search_snippets",
    description="Search Google for a query and return the top search results",
    func=top10_results,
)
llm_with_tools = llm.bind_tools([google_search_results])


def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


tool_node = ToolNode(tools=[google_search_results])
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")
graph = graph_builder.compile()


def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)


def main_event_loop():
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            return False
        stream_graph_updates(user_input)
    except Exception as e:
        print(e)
        return False
    return True

if __name__ == "__main__":
    while main_event_loop():
        pass
