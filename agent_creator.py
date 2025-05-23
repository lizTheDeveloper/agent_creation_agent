from agents import Agent, function_tool, set_tracing_disabled
from agents.extensions.models.litellm_model import LitellmModel
from agents.mcp import MCPServerStdio
from agents import Runner
import random
import os
from typing_extensions import TypedDict, Any
import json
import litellm 
from agents.extensions.models.litellm_model import LitellmModel

## thhings we need:
# - a place to store agents that are generated
# - a place to store tools that are generated
# - an agent that can create agents - agent creator
# - an agent that can create tools - tool creator
# - an agent that can kick off other agents - orchestration agent
# - an agent that can evaluate agents or tools - evaluation agent

litellm.register_model(model_cost={
    "ollama_chat/qwq": { 
        "supports_function_calling": True
    },
})


agents = {}
tools = {}

if os.path.exists("agents.json"):
    ## import all agents from agents.json
    with open("agents.json", "r") as f:
        agents = json.load(f)

if os.path.exists("tools"):
    ## import all tools from the /tools folder, they are python files
    for file in os.listdir("tools"):
        if file.endswith(".py"):
            with open(f"tools/{file}", "r") as f:
                ## eval the file, then import all the functions from the file individually
                exec(f.read())
                for name, func in list(locals().items()):
                    if callable(func):
                        tools[name] = func


class AgentDefinition(TypedDict):
    name: str
    instructions: str
    tools: list[str]

@function_tool
async def create_agent(name: str, instructions: str, tools: list[str]) -> AgentDefinition:
    """Create an agent with the given name, instructions, and tools."""
    ## create a new agent
    agent = Agent(
        name=name,
        instructions=instructions,
        tools=tools
    )
    
    ## save the agent to the agents dictionary
    agents[name] = {
        "name": name,
        "instructions": instructions,
        "tools": tools
    }
    ## save the agent to the agents.json file
    with open("agents.json", "w") as f:
        json.dump(agents, f)
    ## return the agent
    return agent


@function_tool
async def review_agent(agent_name: str) -> str:
    """Review an agent and improve it."""
    ## get the agent
    agent = agents[agent_name]
    return {
        "name": agent_name,
        "instructions": agent["instructions"],
        "tools": agent["tools"]
    }
    

@function_tool
async def create_tool(name: str, python_code: str, description: str) -> str:
    """Create a tool with the given name, python code, and description."""
    ## create a new tool
    tool = {
        "name": name,
        "python_code": python_code,
        "description": description
    }
    ## save the tool to the tools dictionary
    tools[name] = tool
    ## save it  to the /tools folder
    with open(f"tools/{name}.py", "w") as f:
        f.write(python_code)
    ## return the tool
    
    print(f"Tool {name} created successfully.", tool)
    return tool

@function_tool
async def review_tool(tool_name: str) -> str:
    """Review a tool to improve it."""
    ## get the tool from the tools folder
    with open(f"tools/{tool_name}.py", "r") as f:
        tool = f.read()
    return tool


@function_tool
async def recruit_agent(agent_name: str, task: str) -> dict:
    """Recruit an existing agent to perform a specific task."""
    if agent_name not in agents:
        return {"status": "error", "message": f"Agent {agent_name} not found"}
    
    # Get agent details
    agent_info = agents[agent_name]
    
    # This returns the agent info, in a real implementation you would
    # actually run the agent on the task
    return {
        "status": "success",
        "agent_name": agent_name,
        "agent_info": agent_info,
        "task": task,
        "message": f"Agent {agent_name} has been recruited for task: {task}"
    }


@function_tool
async def orchestrate_task(task_description: str) -> dict:
    """Orchestrate a task by identifying required agents and either recruiting them or creating new ones."""
    # First identify which agents might be needed
    agent_requirements = await identify_required_agents(task_description)
    
    results = {
        "task": task_description,
        "agent_requirements": agent_requirements,
        "actions_taken": [],
        "outcome": ""
    }
    
    if agent_requirements["recommendation"] == "use_existing":
        # Use existing agents
        for agent_name in agent_requirements["required_existing_agents"]:
            recruit_result = await recruit_agent(agent_name, task_description)
            results["actions_taken"].append({
                "action": "recruit",
                "agent": agent_name,
                "result": recruit_result
            })
        results["outcome"] = "Existing agents have been recruited for the task."
    
    elif agent_requirements["recommendation"] == "create_new":
        # Need to create new agents
        results["outcome"] = "New agents need to be created for this task."
        for agent_name in agent_requirements["potential_new_agents"]:
            results["actions_taken"].append({
                "action": "suggest_creation",
                "agent": agent_name,
                "message": f"Recommend creating a new agent: {agent_name}"
            })
    
    else:
        # Unclear what to do
        results["outcome"] = "Unable to determine appropriate agents for this task. Please provide more specific information."
    
    return results


async def main():
    set_tracing_disabled(True)
    async with MCPServerStdio(
            params={
                "command": "npx",
                "args": ["-y", "tavily-mcp@0.1.4"],
                "env": {
                    "TAVILY_API_URL": "https://api.tavily.com/v1",
                    "TAVILY_API_KEY": os.getenv("TAVILY_API_KEY"),
                }
            }
        ) as server:

            agent_creator_system_prompt = f"""
                You create agents based on the user's request. Use your tools to create any required agents.
                Give specific, detailed instructions for the agent's system prompt. Make sure to include any information an agent might need, such as the process they'll need to follow, or any context about their purpose.
                Give the name for any tools you need them to have access to, tools will be fetched or created based on the name.
                
                Currently, these agents already exist:
                {[agent['name'] for agent in agents.values()]}
                
                Don't create an agent that already exists, instead, inform the user that the agent already exists.
                
                You have access to search the internet using Tavily to find more information that might help you create the best agent.
                Don't confirm with the user about anything, just create the agent.
                """
            #print(agent_creator_system_prompt)
        
            agent_creator = Agent(
                name="Agent Creator",
                instructions=agent_creator_system_prompt,
                tools=[create_agent],
                mcp_servers=[server],
            )
            result = await Runner.run(agent_creator, "Create an agent that can use the pgvector_rag_query tool to search for curriculum documents. The agent should be able to take a query and return the top 5 most relevant documents from the curriculum.")
            print(result.final_output)
            
            # reviewer_agent = Agent(
            #     name=agents["AgentReviewer"]["name"],
            #     instructions=agents["AgentReviewer"]["instructions"],
            #     tools=[review_agent, create_agent],
            #     mcp_servers=[server],
            # )
            # agent_name = "ToolCreatorAgent"
            # result = await Runner.run(reviewer_agent, f"Review, improve, and recreate the agent: {agent_name}")
            # print(result.final_output)
            # return result.final_output
            
            # tool_creator_agent = Agent(
            #     name="ToolCreatorAgent",
            #     instructions=agents["ToolCreatorAgent"]["instructions"],
            #     tools=[create_tool],
            #     mcp_servers=[server],
            #     model=LitellmModel(model="ollama_chat/qwq")
            # )
            # result = await Runner.run(agent, "Create a tool that uses a pgvector index to implement a RAG system. Use your tools to create the tool.")
            # print(result.final_output)
            # return result.final_output
            
            # tool_reviewer_agent = Agent(
            #     name="ToolReviewer",
            #     instructions=agents["ToolReviewer"]["instructions"],
            #     tools=[review_tool, create_tool],
            #     mcp_servers=[server],
            # )
            # result = await Runner.run(tool_reviewer_agent, "Review shadertoy_example_search. Rewrite the tool. Do not give instructions to the user. Do not reply to the user. Just rewrite the tool.")
            # print(result.final_output)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())