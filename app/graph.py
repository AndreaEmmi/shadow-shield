from langgraph.graph import StateGraph, END
from app.state import AgentState
from app.nodes import anonymize_node, call_llm_node, deanonymize_node

workflow = StateGraph(AgentState)

workflow.add_node("anonymize", anonymize_node)
workflow.add_node("call_llm", call_llm_node)
workflow.add_node("deanonymize", deanonymize_node)

workflow.set_entry_point("anonymize")
workflow.add_edge("anonymize", "call_llm")
workflow.add_edge("call_llm", "deanonymize")
workflow.add_edge("deanonymize", END)

app_graph = workflow.compile()
