import os
import re
import json
from typing import Dict, Any
from fastapi import HTTPException
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.state import AgentState
from app.prompts import SYSTEM_PROMPT
import app.config as config

async def anonymize_node(state: AgentState) -> Dict[str, Any]:
    """Anonymization node using local Ollama model."""
    
    ollama_url = os.getenv("OLLAMA_BASE_URL", config.OLLAMA_BASE_URL).rstrip("/")
    ollama_model = os.getenv("OLLAMA_MODEL", config.OLLAMA_MODEL)
    
    try:
        llm = ChatOllama(
            base_url=ollama_url,
            model=ollama_model,
            format="json",
            temperature=0.0,
        )
        
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=state["original_text"])
        ]
        
        response = await llm.ainvoke(messages)
        response_text = response.content.strip()
        
        parsed_response = json.loads(response_text)
        anonymized_text = parsed_response.get("anonymized_text", state["original_text"])
        mapping = parsed_response.get("mapping", {})

        print(f"ANONYMIZED TEXT:\n'{anonymized_text}' \n")
        
        return {
            "anonymized_text": anonymized_text,
            "mapping": mapping
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during anonymization with ChatOllama: {str(e)}")


async def call_llm_node(state: AgentState) -> Dict[str, Any]:
    """Cloud LLM node that sends anonymized text to OpenRouter."""
    
    api_key = os.getenv("OPENROUTER_API_KEY", config.OPENROUTER_API_KEY)
    model = os.getenv("OPENROUTER_MODEL", config.OPENROUTER_MODEL)

    
    if not api_key:
        raise HTTPException(
            status_code=500, 
            detail="OpenRouter API Key not configured in .env file."
        )
        
    try:
        llm = ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            model=model,
            temperature=0.7
        )
        
        messages = [
            HumanMessage(content=state["anonymized_text"])
        ]
        
        response = await llm.ainvoke(messages)
        llm_response = response.content
        
        print(f"CLOUD AI RESPONSE:\n'{llm_response}' \n")
        
        return {"llm_response": llm_response}
        
    except Exception as e:
        print(f"[OPENAI ERROR] {e}")
        raise HTTPException(status_code=502, detail=f"Failed to communicate with OpenRouter via ChatOpenAI: {str(e)}")


async def deanonymize_node(state: AgentState) -> Dict[str, Any]:
    """De-anonymization node that restores original sensitive values in the LLM response."""
    
    deanonymized_response = state["llm_response"]
    mapping = state["mapping"]
    
    # Case-insensitive replacement for each registered placeholder
    for placeholder, real_val in mapping.items():
        pattern = re.compile(re.escape(placeholder), re.IGNORECASE)
        deanonymized_response = pattern.sub(real_val, deanonymized_response)
        
    print(f"FINAL RESPONSE:\n'{deanonymized_response}'\n")
    
    return {"deanonymized_response": deanonymized_response}
