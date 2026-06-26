"""
Tool name router — dispatches a tool_use block to the correct function.

Add a new elif for every new tool. Never inline this logic in run_conversation.
"""
from tools.fornecedor import consultar_fornecedor
from tools.lista_bloqueio import consultar_lista_bloqueio
from tools.preco_medio import consultar_preco_medio
from tools.web_search import web_search


def run_tool(tool_name: str, tool_input: dict):
    if tool_name == "consultar_fornecedor":
        return consultar_fornecedor(**tool_input)
    elif tool_name == "consultar_lista_bloqueio":
        return consultar_lista_bloqueio(**tool_input)
    elif tool_name == "consultar_preco_medio":
        return consultar_preco_medio(**tool_input)
    elif tool_name == "web_search":
        return web_search(**tool_input)
    else:
        raise ValueError(f"Unknown tool: '{tool_name}'")
