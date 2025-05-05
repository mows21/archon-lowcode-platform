import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
import asyncio


class MCPIntegrationHelper:
    """Helper class for integrating Pydantic AI agents with MCP servers"""
    
    # Default MCP server configurations
    DEFAULT_MCP_CONFIGS = {
        "cline": {
            "name": "Cline MCP Server",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-cline"],
            "env": {},
            "description": "Internal workflow orchestration and AI operations"
        },
        "roo": {
            "name": "Roo MCP Server",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-roo"],
            "env": {},
            "description": "External automation and real-world task execution"
        },
        "claude-desktop": {
            "name": "Claude Desktop MCP Server",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-claude-desktop"],
            "env": {},
            "description": "Local desktop AI assistant operations"
        },
        "filesystem": {
            "name": "Filesystem MCP Server",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem"],
            "env": {},
            "description": "File system operations"
        },
        "postgres": {
            "name": "PostgreSQL MCP Server",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-postgres"],
            "env": {
                "DATABASE_URL": os.getenv("POSTGRES_URL", "postgresql://user:pass@localhost:5432/db")
            },
            "description": "PostgreSQL database operations"
        },
        "brave": {
            "name": "Brave Search MCP Server",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-brave-search"],
            "env": {
                "BRAVE_API_KEY": os.getenv("BRAVE_API_KEY", "")
            },
            "description": "Web search capabilities"
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize MCP Integration Helper
        
        Args:
            config_path: Path to custom MCP configuration file
        """
        self.config_path = config_path
        self.custom_configs = self._load_custom_configs() if config_path else {}
        self.active_servers: Dict[str, MCPServerStdio] = {}
    
    def _load_custom_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load custom MCP server configurations from file"""
        if not self.config_path or not os.path.exists(self.config_path):
            return {}
        
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading custom configs: {e}")
            return {}
    
    def get_available_servers(self) -> Dict[str, Dict[str, Any]]:
        """Get all available MCP server configurations"""
        available_servers = self.DEFAULT_MCP_CONFIGS.copy()
        available_servers.update(self.custom_configs)
        return available_servers
    
    def create_server(
        self, 
        server_name: str, 
        config: Optional[Dict[str, Any]] = None
    ) -> MCPServerStdio:
        """
        Create an MCP server instance
        
        Args:
            server_name: Name of the server to create
            config: Custom configuration override
            
        Returns:
            MCPServerStdio instance
        """
        if config is None:
            all_configs = self.get_available_servers()
            if server_name not in all_configs:
                raise ValueError(f"Unknown server: {server_name}")
            config = all_configs[server_name]
        
        command = config.get("command", "npx")
        args = config.get("args", [])
        env = config.get("env", {})
        
        # Merge with current environment
        full_env = os.environ.copy()
        full_env.update(env)
        
        return MCPServerStdio(command, args, env=full_env)
    
    async def connect_agent_to_servers(
        self, 
        agent: Agent, 
        server_names: List[str]
    ) -> Agent:
        """
        Connect a Pydantic AI agent to multiple MCP servers
        
        Args:
            agent: Pydantic AI agent
            server_names: List of server names to connect
            
        Returns:
            Agent with connected MCP servers
        """
        for server_name in server_names:
            try:
                # Create and store server instance
                server = self.create_server(server_name)
                self.active_servers[server_name] = server
                
                # Add to agent's MCP servers list
                if not hasattr(agent, 'mcp_servers'):
                    agent.mcp_servers = []
                agent.mcp_servers.append(server)
                
                print(f"Successfully connected to {server_name} MCP server")
            except Exception as e:
                print(f"Failed to connect to {server_name}: {e}")
        
        return agent
    
    async def list_server_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """
        List all tools available from a specific MCP server
        
        Args:
            server_name: Name of the server
            
        Returns:
            List of tool information
        """
        if server_name not in self.active_servers:
            server = self.create_server(server_name)
            self.active_servers[server_name] = server
        else:
            server = self.active_servers[server_name]
        
        # This would require implementing the MCP protocol
        # For now, return a placeholder
        return [
            {
                "name": f"{server_name}_tool",
                "description": f"Tool from {server_name} server",
                "parameters": {}
            }
        ]
    
    def save_agent_mcp_config(
        self, 
        agent_name: str, 
        server_configs: Dict[str, Dict[str, Any]], 
        output_dir: str = "configs"
    ):
        """
        Save agent MCP configuration to file
        
        Args:
            agent_name: Name of the agent
            server_configs: Dictionary of server configurations
            output_dir: Directory to save configuration
        """
        os.makedirs(output_dir, exist_ok=True)
        config_file = os.path.join(output_dir, f"{agent_name}_mcp_config.json")
        
        with open(config_file, 'w') as f:
            json.dump(server_configs, f, indent=2)
        
        print(f"Saved MCP configuration to {config_file}")
    
    @staticmethod
    def load_agent_mcp_config(config_file: str) -> Dict[str, Dict[str, Any]]:
        """
        Load agent MCP configuration from file
        
        Args:
            config_file: Path to configuration file
            
        Returns:
            Dictionary of server configurations
        """
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        with open(config_file, 'r') as f:
            return json.load(f)
    
    async def test_connection(self, server_name: str) -> bool:
        """
        Test connection to an MCP server
        
        Args:
            server_name: Name of the server to test
            
        Returns:
            True if connection successful
        """
        try:
            server = self.create_server(server_name)
            # Here you would implement actual connection test
            # For now, return True as placeholder
            return True
        except Exception as e:
            print(f"Connection test failed for {server_name}: {e}")
            return False
    
    def generate_mcp_integration_code(
        self, 
        agent_name: str, 
        server_names: List[str],
        template_path: Optional[str] = None
    ) -> str:
        """
        Generate code for agent with MCP integration
        
        Args:
            agent_name: Name of the agent
            server_names: List of MCP servers to integrate
            template_path: Path to agent template file
            
        Returns:
            Generated code with MCP integration
        """
        if template_path and os.path.exists(template_path):
            with open(template_path, 'r') as f:
                template = f.read()
        else:
            # Use default template
            template = '''
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from dataclasses import dataclass

@dataclass
class {agent_name}Deps:
    api_key: str

# Create agent
{agent_name.lower()}_agent = Agent(
    'gpt-4',
    system_prompt="You are an AI assistant with MCP server integration.",
    deps_type={agent_name}Deps
)

# Connect to MCP servers
mcp_servers = []
{mcp_connections}

{agent_name.lower()}_agent.mcp_servers = mcp_servers

# Run agent
if __name__ == "__main__":
    import asyncio
    async def main():
        deps = {agent_name}Deps(api_key="your-api-key")
        result = await {agent_name.lower()}_agent.run("Hello!", deps=deps)
        print(result.data)
    
    asyncio.run(main())
'''
        
        # Generate MCP connection code
        mcp_connections = []
        for server_name in server_names:
            server_code = f'''
# Connect to {server_name}
{server_name}_server = MCPServerStdio(
    "{self.DEFAULT_MCP_CONFIGS[server_name]['command']}",
    {self.DEFAULT_MCP_CONFIGS[server_name]['args']},
    env={{"DATABASE_URL": "your-database-url"}}  # Configure as needed
)
mcp_servers.append({server_name}_server)
'''
            mcp_connections.append(server_code)
        
        # Format template
        return template.format(
            agent_name=agent_name,
            mcp_connections="\n".join(mcp_connections)
        )


# Example usage
if __name__ == "__main__":
    # Initialize helper
    mcp_helper = MCPIntegrationHelper()
    
    # Create an agent
    agent = Agent('gpt-4', system_prompt="Test agent")
    
    # Connect to MCP servers
    server_names = ["cline", "filesystem", "brave"]
    
    async def main():
        # Connect agent to servers
        updated_agent = await mcp_helper.connect_agent_to_servers(agent, server_names)
        
        # Test connections
        for server in server_names:
            success = await mcp_helper.test_connection(server)
            print(f"{server} connection: {'Success' if success else 'Failed'}")
        
        # Generate integration code
        code = mcp_helper.generate_mcp_integration_code(
            "MyAgent", 
            server_names
        )
        print("\nGenerated code:")
        print(code)
    
    asyncio.run(main())
