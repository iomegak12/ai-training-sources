"""
FAISS Service for Agentic RAG API
Singleton service for FAISS vector store initialization and retrieval
"""
import os
from pathlib import Path
from typing import Optional, List
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool
from config.settings import settings
from config.logging_config import get_logger

logger = get_logger(__name__)


class FAISSService:
    """
    Singleton service for managing FAISS vector store
    
    Handles:
    - One-time initialization from configured URLs
    - Document loading and chunking
    - FAISS index creation
    - Retriever tool creation
    - Optional disk persistence
    """
    
    _instance: Optional['FAISSService'] = None
    _initialized: bool = False
    
    def __new__(cls):
        """Singleton pattern: ensure only one instance exists"""
        if cls._instance is None:
            cls._instance = super(FAISSService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize FAISS service (only once)"""
        if not FAISSService._initialized:
            self.vectorstore: Optional[FAISS] = None
            self.retriever = None
            self.retriever_tool = None
            self.embeddings = None
            FAISSService._initialized = True
            logger.info("FAISSService instance created")
    
    def initialize(self) -> bool:
        """
        Initialize FAISS vector store from configured URLs
        
        Returns:
            True if successful, False otherwise
        """
        if self.vectorstore is not None:
            logger.info("FAISS vector store already initialized")
            return True
        
        try:
            logger.info("=" * 60)
            logger.info("FAISS INITIALIZATION")
            logger.info("=" * 60)
            
            # Get URLs from settings
            urls = settings.faiss_urls_list
            
            if not urls:
                logger.error("No URLs configured for FAISS initialization")
                return False
            
            logger.info(f"Loading documents from {len(urls)} URL(s)...")
            for i, url in enumerate(urls, 1):
                logger.info(f"  {i}. {url}")
            
            # Load documents from all URLs
            all_docs = []
            for url in urls:
                try:
                    logger.info(f"Loading: {url}")
                    loader = WebBaseLoader(url)
                    docs = loader.load()
                    all_docs.extend(docs)
                    logger.info(f"  ✓ Loaded {len(docs)} document(s)")
                except Exception as e:
                    logger.warning(f"  ✗ Failed to load {url}: {str(e)}")
                    continue
            
            if not all_docs:
                logger.error("No documents loaded from any URL")
                return False
            
            logger.info(f"Total documents loaded: {len(all_docs)}")
            
            # Split documents into chunks
            logger.info("Splitting documents into chunks...")
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.faiss_chunk_size,
                chunk_overlap=settings.faiss_chunk_overlap
            )
            documents = text_splitter.split_documents(all_docs)
            logger.info(f"  ✓ Created {len(documents)} chunks")
            
            # Create embeddings
            logger.info("Initializing OpenAI embeddings...")
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=settings.openai_api_key
            )
            
            # Create FAISS vector store
            logger.info("Creating FAISS vector store (this may take a moment)...")
            self.vectorstore = FAISS.from_documents(documents, self.embeddings)
            logger.info("  ✓ FAISS vector store created")
            
            # Save to disk if caching is enabled
            if settings.faiss_cache_enabled:
                cache_path = settings.faiss_cache_path
                cache_dir = cache_path.parent
                cache_dir.mkdir(parents=True, exist_ok=True)
                
                logger.info(f"Saving FAISS index to disk: {cache_path}")
                self.vectorstore.save_local(str(cache_path))
                logger.info("  ✓ FAISS index saved to disk")
            
            # Create retriever
            self.retriever = self.vectorstore.as_retriever()
            logger.info("  ✓ Retriever created")
            
            # Create retriever tool
            self.retriever_tool = create_retriever_tool(
                self.retriever,
                settings.faiss_tool_name,
                settings.faiss_tool_description
            )
            logger.info(f"  ✓ Retriever tool created: '{settings.faiss_tool_name}'")
            
            logger.info("=" * 60)
            logger.info("FAISS INITIALIZATION COMPLETE ✓")
            logger.info(f"  Documents: {len(all_docs)}")
            logger.info(f"  Chunks: {len(documents)}")
            logger.info(f"  Tool: {self.retriever_tool.name}")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"Error initializing FAISS: {str(e)}", exc_info=True)
            return False
    
    def load_from_disk(self) -> bool:
        """
        Load FAISS index from disk cache
        
        Returns:
            True if successful, False otherwise
        """
        if self.vectorstore is not None:
            logger.info("FAISS vector store already initialized")
            return True
        
        try:
            cache_path = settings.faiss_cache_path
            
            if not cache_path.exists():
                logger.warning(f"FAISS cache not found at {cache_path}")
                return False
            
            logger.info(f"Loading FAISS index from disk: {cache_path}")
            
            # Initialize embeddings
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=settings.openai_api_key
            )
            
            # Load FAISS index
            self.vectorstore = FAISS.load_local(
                str(cache_path),
                self.embeddings,
                allow_dangerous_deserialization=True  # We trust our own cached data
            )
            logger.info("  ✓ FAISS index loaded from disk")
            
            # Create retriever
            self.retriever = self.vectorstore.as_retriever()
            
            # Create retriever tool
            self.retriever_tool = create_retriever_tool(
                self.retriever,
                settings.faiss_tool_name,
                settings.faiss_tool_description
            )
            logger.info(f"  ✓ Retriever tool created: '{self.retriever_tool.name}'")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading FAISS from disk: {str(e)}", exc_info=True)
            return False
    
    def get_retriever_tool(self):
        """
        Get the retriever tool (initializes if not already done)
        
        Returns:
            Retriever tool for LangChain agent
        """
        if self.retriever_tool is None:
            # Try to load from cache first
            if settings.faiss_cache_enabled:
                success = self.load_from_disk()
                if not success:
                    logger.info("Cache load failed, initializing from URLs...")
                    self.initialize()
            else:
                self.initialize()
        
        return self.retriever_tool
    
    def is_ready(self) -> bool:
        """
        Check if FAISS service is ready to use
        
        Returns:
            True if initialized, False otherwise
        """
        return self.retriever_tool is not None
    
    def get_info(self) -> dict:
        """
        Get information about FAISS service status
        
        Returns:
            Dictionary with status information
        """
        return {
            'initialized': self.is_ready(),
            'vectorstore_type': 'FAISS' if self.vectorstore else None,
            'tool_name': self.retriever_tool.name if self.retriever_tool else None,
            'cache_enabled': settings.faiss_cache_enabled,
            'cache_path': str(settings.faiss_cache_path) if settings.faiss_cache_enabled else None
        }


# Singleton instance - export for easy access
faiss_service = FAISSService()
