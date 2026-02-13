"""
Agent Service for Agentic RAG API
Manages LangGraph ReAct agent with all tools
"""
from typing import Optional, List, Dict, Any, AsyncIterator
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from config.settings import settings
from config.logging_config import get_logger
from tools.search_tools import get_all_search_tools
from tools.crm_tools import get_all_crm_tools
from tools.sql_tools import get_sql_tool
from services.faiss_service import faiss_service

logger = get_logger(__name__)


class AgentService:
    """
    Service for managing LangGraph ReAct agent
    
    Responsibilities:
    - Initialize LLM
    - Load all tools (search, CRM, SQL, FAISS)
    - Create ReAct agent executor
    - Handle invoke (blocking) and stream (async) operations
    - Manage conversation state
    """
    
    _instance: Optional['AgentService'] = None
    _initialized: bool = False
    
    def __new__(cls):
        """Singleton pattern: ensure only one instance exists"""
        if cls._instance is None:
            cls._instance = super(AgentService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize Agent service (only once)"""
        if not AgentService._initialized:
            self.llm: Optional[ChatOpenAI] = None
            self.tools: List = []
            self.agent_executor = None
            self.system_message: Optional[str] = settings.agent_system_message
            AgentService._initialized = True
            logger.info("AgentService instance created")
    
    def initialize(self) -> bool:
        """
        Initialize agent with LLM and all tools
        
        Returns:
            True if successful, False otherwise
        """
        if self.agent_executor is not None:
            logger.info("Agent executor already initialized")
            return True
        
        try:
            logger.info("=" * 60)
            logger.info("AGENT INITIALIZATION")
            logger.info("=" * 60)
            
            # Initialize LLM
            logger.info(f"Initializing LLM: {settings.agent_model_name}")
            self.llm = ChatOpenAI(
                model=settings.agent_model_name,
                max_tokens=settings.agent_max_tokens,
                temperature=settings.agent_temperature,
                openai_api_key=settings.openai_api_key
            )
            logger.info("  ✓ LLM initialized")
            
            # Load all tools
            logger.info("Loading tools...")
            
            # 1. Search tools (Wikipedia, ArXiv, DuckDuckGo)
            search_tools = get_all_search_tools()
            logger.info(f"  ✓ Search tools: {len(search_tools)}")
            
            # 2. CRM tools (5 business client tools)
            crm_tools = get_all_crm_tools()
            logger.info(f"  ✓ CRM tools: {len(crm_tools)}")
            
            # 3. SQL tool (Chinook database)
            sql_tool = get_sql_tool()
            logger.info(f"  ✓ SQL tool: 1")
            
            # 4. FAISS retriever tool
            logger.info("  Initializing FAISS retriever tool...")
            retriever_tool = faiss_service.get_retriever_tool()
            if retriever_tool:
                logger.info(f"  ✓ FAISS tool: 1 ('{retriever_tool.name}')")
            else:
                logger.warning("  ✗ FAISS tool initialization failed (continuing without it)")
                retriever_tool = []
            
            # Combine all tools
            self.tools = search_tools + crm_tools + [sql_tool]
            if retriever_tool:
                self.tools.append(retriever_tool)
            
            logger.info(f"Total tools loaded: {len(self.tools)}")
            logger.info("\nTools available:")
            for i, tool in enumerate(self.tools, 1):
                logger.info(f"  {i}. {tool.name}")
            
            # Create ReAct agent executor
            logger.info("\nCreating LangGraph ReAct agent...")
            self.agent_executor = create_react_agent(
                self.llm,
                tools=self.tools
            )
            logger.info("  ✓ ReAct agent created")
            
            logger.info("=" * 60)
            logger.info("AGENT INITIALIZATION COMPLETE ✓")
            logger.info(f"  Model: {settings.agent_model_name}")
            logger.info(f"  Tools: {len(self.tools)}")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"Error initializing agent: {str(e)}", exc_info=True)
            return False
    
    def invoke(self, message: str, conversation_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Invoke agent with a message (blocking call)
        
        Args:
            message: User message/question
            conversation_history: Optional list of previous messages
                                 Format: [{"role": "user|assistant", "content": "..."}]
        
        Returns:
            Dictionary with full response including message history
        """
        if self.agent_executor is None:
            self.initialize()
        
        try:
            # Build message list
            messages = []
            
            # Add system message if configured
            if self.system_message:
                messages.append(SystemMessage(content=self.system_message))
            
            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history:
                    if msg.get("role") == "user":
                        messages.append(HumanMessage(content=msg.get("content", "")))
                    elif msg.get("role") == "assistant":
                        messages.append(AIMessage(content=msg.get("content", "")))
            
            # Add current message
            messages.append(HumanMessage(content=message))
            
            # Invoke agent
            logger.info(f"Invoking agent with message: {message[:100]}...")
            result = self.agent_executor.invoke({"messages": messages})
            
            logger.info("Agent invocation complete")
            return result
            
        except Exception as e:
            logger.error(f"Error invoking agent: {str(e)}", exc_info=True)
            raise
    
    async def stream(self, message: str, conversation_history: Optional[List[Dict]] = None) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream agent responses (async generator)
        
        Args:
            message: User message/question
            conversation_history: Optional list of previous messages
        
        Yields:
            Dictionary chunks with agent and tool outputs
            Format: {"agent": {...}} or {"tools": {...}}
        """
        if self.agent_executor is None:
            self.initialize()
        
        try:
            # Build message list
            messages = []
            
            # Add system message if configured
            if self.system_message:
                messages.append(SystemMessage(content=self.system_message))
            
            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history:
                    if msg.get("role") == "user":
                        messages.append(HumanMessage(content=msg.get("content", "")))
                    elif msg.get("role") == "assistant":
                        messages.append(AIMessage(content=msg.get("content", "")))
            
            # Add current message
            messages.append(HumanMessage(content=message))
            
            # Stream agent responses
            logger.info(f"Streaming agent response for message: {message[:100]}...")
            
            async for chunk in self.agent_executor.astream({"messages": messages}):
                yield chunk
            
            logger.info("Agent streaming complete")
            
        except Exception as e:
            logger.error(f"Error streaming agent response: {str(e)}", exc_info=True)
            raise
    
    def get_tools_info(self) -> List[Dict[str, str]]:
        """
        Get information about all available tools
        
        Returns:
            List of tool information dictionaries
        """
        if not self.tools:
            self.initialize()
        
        tools_info = []
        for tool in self.tools:
            tools_info.append({
                "name": tool.name,
                "description": tool.description
            })
        
        return tools_info
    
    def is_ready(self) -> bool:
        """
        Check if agent is ready to use
        
        Returns:
            True if initialized, False otherwise
        """
        return self.agent_executor is not None
    
    def get_info(self) -> dict:
        """
        Get information about agent service status
        
        Returns:
            Dictionary with status information
        """
        return {
            'initialized': self.is_ready(),
            'model': settings.agent_model_name if self.llm else None,
            'tools_count': len(self.tools),
            'tools': [t.name for t in self.tools] if self.tools else [],
            'system_message': self.system_message
        }


# Singleton instance - export for easy access
agent_service = AgentService()
