from pydantic_ai import Agent
from dataclasses import dataclass
import os
from typing import List, Dict, Any, Optional

# ARCHON Agent Template - Basic
# Generated with visual builder
# Modify sections marked with # TODO: for customization

@dataclass
class AgentDeps:
    """Dependencies for the agent"""
    # TODO: Add your custom dependencies here
    api_key: str
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 1000
    custom_data: Optional[Dict[str, Any]] = None

class BasicAgentTemplate:
    """Basic agent template for general-purpose AI tasks"""
    
    def __init__(self, deps: AgentDeps):
        self.deps = deps
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create the Pydantic AI agent"""
        
        # TODO: Customize system prompt for your use case
        system_prompt = """You are a helpful AI assistant created by ARCHON.
        Your capabilities are determined by the tools and configurations provided.
        Always be helpful, accurate, and concise in your responses.
        
        Key Guidelines:
        1. Provide clear and actionable responses
        2. Ask for clarification when needed
        3. Use tools appropriately
        4. Maintain a professional tone
        """
        
        agent = Agent(
            self.deps.model,
            system_prompt=system_prompt,
            deps_type=AgentDeps,
            settings={
                "temperature": self.deps.temperature,
                "max_tokens": self.deps.max_tokens
            }
        )
        
        # Add default tools
        self._add_tools(agent)
        
        return agent
    
    def _add_tools(self, agent: Agent):
        """Add tools to the agent"""
        
        # TODO: Add custom tools here
        
        @agent.tool
        async def get_information(ctx, topic: str) -> str:
            """
            Get information about a specific topic
            
            Args:
                topic: The topic to get information about
                
            Returns:
                Information about the topic
            """
            # TODO: Implement tool logic
            return f"Information about {topic}: This is a placeholder response."
        
        @agent.tool
        async def process_data(ctx, data: Dict[str, Any]) -> Dict[str, Any]:
            """
            Process structured data
            
            Args:
                data: The data to process
                
            Returns:
                Processed data
            """
            # TODO: Implement data processing logic
            processed = data.copy()
            processed["processed"] = True
            return processed
    
    async def run(self, message: str) -> str:
        """
        Run the agent with a message
        
        Args:
            message: User message to process
            
        Returns:
            Agent response
        """
        result = await self.agent.run(message, deps=self.deps)
        return result.data

# Example usage
if __name__ == "__main__":
    # Configure agent dependencies
    deps = AgentDeps(
        api_key=os.getenv("OPENAI_API_KEY", ""),
        model="gpt-4",
        temperature=0.7,
        max_tokens=1000
    )
    
    # Create and run agent
    basic_agent = BasicAgentTemplate(deps)
    
    async def main():
        response = await basic_agent.run("Hello! Tell me about AI agents.")
        print(f"Agent Response: {response}")
    
    # Run the agent
    import asyncio
    asyncio.run(main())
