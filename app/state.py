from typing import TypedDict, Dict

class AgentState(TypedDict):
    original_text: str
    anonymized_text: str
    mapping: Dict[str, str]
    llm_response: str
    deanonymized_response: str
