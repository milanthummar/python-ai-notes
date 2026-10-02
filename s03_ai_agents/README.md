# 3. AI / agents

Everything here runs offline: no API keys, no LLM calls. Each chunk builds the
mechanism in plain Python so it can be tested.

1. [RAG](c01_rag/) — chunk, embed, retrieve, build the prompt
2. [LLM fundamentals](c02_llm_fundamentals/) — logits, softmax, temperature, greedy vs sampling
3. [LangGraph vs LangChain](c03_langgraph_vs_langchain/) — a tiny state graph vs a chain
4. [Tool calling](c04_tool_calling/) — schemas, validated dispatch, errors as results
5. [MCP vs A2A](c05_mcp_vs_a2a/) — JSON-RPC tool server vs agent task lifecycle
