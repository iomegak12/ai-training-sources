/**
 * Chat Page JavaScript
 * Handles chat interface, API communication, conversation history
 */

class ChatManager {
    constructor() {
        this.conversationHistory = [];
        this.isProcessing = false;
        this.apiUrl = window.AppUtils.CONFIG.API_URL;
        
        // DOM elements
        this.chatMessages = document.getElementById('chat-messages');
        this.chatForm = document.getElementById('chat-form');
        this.chatInput = document.getElementById('chat-input');
        this.sendButton = document.getElementById('send-button');
        this.clearButton = document.getElementById('clear-chat');
        this.scrollDownButton = document.getElementById('scroll-down');
        
        this.init();
    }

    init() {
        // Check if all required elements exist (only on chat page)
        if (!this.chatMessages || !this.chatForm || !this.chatInput || !this.sendButton) {
            console.warn('Chat elements not found - skipping chat initialization');
            return;
        }
        
        // Set up event listeners
        this.chatForm.addEventListener('submit', (e) => this.handleSubmit(e));
        
        if (this.clearButton) {
            this.clearButton.addEventListener('click', () => this.clearChat());
        }
        
        if (this.scrollDownButton) {
            this.scrollDownButton.addEventListener('click', () => this.scrollToBottom(true));
        }
        
        // Auto-resize textarea
        this.chatInput.addEventListener('input', () => this.autoResizeTextarea());
        
        // Handle Enter key (Shift+Enter for new line, Enter to send)
        this.chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.chatForm.requestSubmit();
            }
        });
        
        // Show/hide scroll down button
        this.chatMessages.addEventListener('scroll', () => this.handleScroll());
        
        // Load conversation history from session storage
        this.loadConversationHistory();
        
        // Show welcome message if no history
        if (this.conversationHistory.length === 0) {
            this.showWelcomeMessage();
        }
        
        console.log('💬 Chat initialized');
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        console.log('📨 Form submitted');
        
        const question = this.chatInput.value.trim();
        console.log('❓ Question:', question);
        
        if (!question || this.isProcessing) {
            console.log('⚠️ Empty question or already processing');
            return;
        }
        
        // Add user message to chat
        this.addMessage({
            type: 'user',
            content: question,
            timestamp: new Date().toISOString()
        });
        
        // Clear input and reset height
        this.chatInput.value = '';
        this.autoResizeTextarea();
        
        // Set processing state
        this.setProcessing(true);
        
        // Show typing indicator
        const typingIndicator = this.showTypingIndicator();
        
        try {
            console.log('🔄 Calling API...');
            // Call API
            const response = await this.queryAgent(question);
            console.log('✅ API Response:', response);
            
            // Remove typing indicator
            this.removeTypingIndicator(typingIndicator);
            
            // Add assistant message
            this.addMessage({
                type: 'assistant',
                content: response.answer,
                tools: response.tools_used || [],
                timestamp: response.timestamp || new Date().toISOString()
            });
            
        } catch (error) {
            console.error('❌ Error:', error);
            
            // Remove typing indicator
            this.removeTypingIndicator(typingIndicator);
            
            // Show error message
            this.addMessage({
                type: 'error',
                content: `Error: ${error.message}`,
                timestamp: new Date().toISOString()
            });
            
            window.AppUtils.showToast(`Failed to get response: ${error.message}`, 'error');
        } finally {
            this.setProcessing(false);
            this.chatInput.focus();
        }
    }

    async queryAgent(question) {
        console.log('🌐 API URL:', this.apiUrl);
        console.log('📤 Sending request to:', `${this.apiUrl}/query`);
        console.log('📦 Payload:', { question });
        
        const response = await fetch(`${this.apiUrl}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question })
        });

        console.log('📥 Response status:', response.status);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            console.error('❌ API Error:', errorData);
            throw new Error(errorData.detail || `API error: ${response.status}`);
        }

        const data = await response.json();
        console.log('✅ Response data:', data);
        return data;
    }

    addMessage(message) {
        // Add to conversation history
        this.conversationHistory.push(message);
        this.saveConversationHistory();
        
        // Create message element
        const messageElement = this.createMessageElement(message);
        this.chatMessages.appendChild(messageElement);
        
        // Scroll to bottom
        this.scrollToBottom();
    }

    createMessageElement(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${message.type}`;
        
        // Create message content
        let contentHtml = `<div class="message-content">${window.AppUtils.formatText(message.content)}</div>`;
        
        // Add tools used if available
        if (message.tools && message.tools.length > 0) {
            const toolsHtml = message.tools
                .map(tool => `<span class="tool-badge"><i class="fas fa-tools"></i> ${window.AppUtils.escapeHtml(tool)}</span>`)
                .join('');
            contentHtml += `<div class="message-tools">${toolsHtml}</div>`;
        }
        
        // Add timestamp
        const timestamp = window.AppUtils.formatTimestamp(message.timestamp);
        contentHtml += `<div class="message-timestamp">${timestamp}</div>`;
        
        // Add copy button for assistant messages
        if (message.type === 'assistant') {
            contentHtml += `
                <button class="message-copy" title="Copy message" aria-label="Copy message">
                    <i class="fas fa-copy"></i>
                </button>
            `;
        }
        
        messageDiv.innerHTML = contentHtml;
        
        // Add copy functionality
        const copyBtn = messageDiv.querySelector('.message-copy');
        if (copyBtn) {
            copyBtn.addEventListener('click', () => {
                window.AppUtils.copyToClipboard(message.content);
            });
        }
        
        return messageDiv;
    }

    showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'message message-assistant typing-indicator';
        indicator.innerHTML = `
            <div class="message-content">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        this.chatMessages.appendChild(indicator);
        this.scrollToBottom();
        return indicator;
    }

    removeTypingIndicator(indicator) {
        if (indicator && indicator.parentNode) {
            indicator.parentNode.removeChild(indicator);
        }
    }

    showWelcomeMessage() {
        const welcomeDiv = document.createElement('div');
        welcomeDiv.className = 'welcome-message';
        welcomeDiv.innerHTML = `
            <div class="welcome-icon">
                <i class="fas fa-robot"></i>
            </div>
            <h2>Welcome to Agentic RAG Assistant</h2>
            <p>I'm an AI-powered research assistant that can help you find information using multiple tools:</p>
            <div class="welcome-tools">
                <div class="welcome-tool">
                    <i class="fas fa-search"></i>
                    <span>Google Search</span>
                </div>
                <div class="welcome-tool">
                    <i class="fab fa-wikipedia-w"></i>
                    <span>Wikipedia</span>
                </div>
                <div class="welcome-tool">
                    <i class="fas fa-book"></i>
                    <span>ArXiv Papers</span>
                </div>
                <div class="welcome-tool">
                    <i class="fas fa-file-alt"></i>
                    <span>Document Search</span>
                </div>
            </div>
            <p class="welcome-prompt">Ask me anything to get started!</p>
        `;
        this.chatMessages.appendChild(welcomeDiv);
    }

    clearChat() {
        if (this.conversationHistory.length === 0) return;
        
        if (confirm('Are you sure you want to clear the conversation history?')) {
            this.conversationHistory = [];
            this.chatMessages.innerHTML = '';
            this.saveConversationHistory();
            this.showWelcomeMessage();
            window.AppUtils.showToast('Conversation cleared', 'success');
        }
    }

    saveConversationHistory() {
        try {
            sessionStorage.setItem('conversationHistory', JSON.stringify(this.conversationHistory));
        } catch (error) {
            console.error('Failed to save conversation history:', error);
        }
    }

    loadConversationHistory() {
        try {
            const saved = sessionStorage.getItem('conversationHistory');
            if (saved) {
                this.conversationHistory = JSON.parse(saved);
                // Render saved messages
                this.conversationHistory.forEach(message => {
                    const messageElement = this.createMessageElement(message);
                    this.chatMessages.appendChild(messageElement);
                });
                this.scrollToBottom();
            }
        } catch (error) {
            console.error('Failed to load conversation history:', error);
            this.conversationHistory = [];
        }
    }

    setProcessing(processing) {
        this.isProcessing = processing;
        this.chatInput.disabled = processing;
        this.sendButton.disabled = processing;
        
        // Update button icon if it exists
        const icon = this.sendButton.querySelector('i');
        if (icon) {
            if (processing) {
                icon.className = 'fas fa-spinner fa-spin';
            } else {
                icon.className = 'fas fa-paper-plane';
            }
        }
        
        // Update button text if it exists
        const text = this.sendButton.querySelector('.send-text');
        if (text) {
            text.textContent = processing ? 'Sending...' : 'Send';
        }
    }

    autoResizeTextarea() {
        this.chatInput.style.height = 'auto';
        const newHeight = Math.min(this.chatInput.scrollHeight, 150); // Max height 150px
        this.chatInput.style.height = newHeight + 'px';
    }

    scrollToBottom(smooth = true) {
        if (smooth) {
            this.chatMessages.scrollTo({
                top: this.chatMessages.scrollHeight,
                behavior: 'smooth'
            });
        } else {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }
    }

    handleScroll() {
        const { scrollTop, scrollHeight, clientHeight } = this.chatMessages;
        const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;
        
        if (isNearBottom) {
            this.scrollDownButton.style.display = 'none';
        } else {
            this.scrollDownButton.style.display = 'flex';
        }
    }
}

// Initialize chat when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if we're on the chat page
    const chatForm = document.getElementById('chat-form');
    if (!chatForm) {
        return; // Not on chat page, skip initialization
    }
    
    const chatManager = new ChatManager();
    
    // Example queries for quick start
    const exampleQueries = [
        "What is quantum computing?",
        "Search for recent papers on artificial intelligence",
        "Tell me about the history of the internet"
    ];
    
    // Add example query buttons (optional)
    const examplesContainer = document.querySelector('.chat-examples');
    if (examplesContainer) {
        exampleQueries.forEach(query => {
            const button = document.createElement('button');
            button.className = 'example-query';
            button.textContent = query;
            button.addEventListener('click', () => {
                chatManager.chatInput.value = query;
                chatManager.chatInput.focus();
            });
            examplesContainer.appendChild(button);
        });
    }
});
