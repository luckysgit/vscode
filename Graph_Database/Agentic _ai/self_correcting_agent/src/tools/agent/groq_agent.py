import json
from groq import Groq
from config.settings import GROQ_API_KEY
from src.database.neo4j_client import db_client
from src.tools.cypher_tools import graph_cypher_traversal
from src.tools.vector_tools import vector_index_search
from src.tools.calc_tools import python_calculator

client = Groq(api_key=GROQ_API_KEY)

TOOL_MAP = {
    "vector_index_search": vector_index_search,
    "graph_cypher_traversal": graph_cypher_traversal,
    "python_calculator": python_calculator
}

groq_tools = [
    {
        "type": "function",
        "function": {
            "name": "vector_index_search",
            "description": "Performs HNSW vector search to find matching document text in Neo4j.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "Search query text"}},
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "graph_cypher_traversal",
            "description": "Searches connected entities and categories in Neo4j.",
            "parameters": {
                "type": "object",
                "properties": {"entity_name": {"type": "string", "description": "Entity or category name to search"}},
                "required": ["entity_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "python_calculator",
            "description": "Evaluates math expressions safely.",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string", "description": "Math expression like '248.85 * 0.15'"}},
                "required": ["expression"]
            }
        }
    }
]

def run_agentic_pipeline(user_goal: str, max_iterations: int = 4):
    """Executes ReAct agent loop with self-correction logic."""
    print(f"🎯 User Goal: {user_goal}\n" + "="*50)
    
    # Initialize Neo4j Schema & Baseline Data
    db_client.initialize_schema_and_data()
    
    system_prompt = """
    You are an AI Agent with tool access. Follow these self-correction rules:
    1. If 'graph_cypher_traversal' returns no matches or a FALLBACK REQUIRED message, DO NOT give up.
    2. Immediately call 'vector_index_search' using relevant keywords as a secondary retrieval strategy.
    3. Synthesize a final answer once tool execution is complete.
    """
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_goal}
    ]
    
    for iteration in range(1, max_iterations + 1):
        print(f"\n🔄 [Iteration {iteration}] Agent Thinking...")
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=groq_tools,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        
        if tool_calls:
            messages.append(response_message)
            for tool_call in tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)
                print(f"🛠️ Agent Action: Executing `{fn_name}` with args: {fn_args}")
                
                if fn_name in TOOL_MAP:
                    tool_output = TOOL_MAP[fn_name](**fn_args)
                    print(f"📥 Tool Output:\n{tool_output}")
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": fn_name,
                        "content": tool_output
                    })
        else:
            print("\n✅ Final Answer Generated:")
            print("-" * 50)
            print(response_message.content.strip())
            return response_message.content.strip()

if __name__ == "__main__":
    run_agentic_pipeline("Search the knowledge graph for Neo4j features and calculate 15% of 248.85s latency.")