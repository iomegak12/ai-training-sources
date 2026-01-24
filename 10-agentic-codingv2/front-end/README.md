# Agentic RAG - Frontend

A professional web application showcasing the Agentic RAG (Retrieval-Augmented Generation) backend API. Built with Node.js, Express, and vanilla JavaScript for a clean, responsive user experience.

## 🎨 Features

- **Multi-Page Navigation**: Home, Chat, About, and Contact pages
- **Interactive Chat Interface**: Real-time conversation with AI assistant
- **Tool Transparency**: Display which tools (Google, Wikipedia, ArXiv, Documents) were used
- **Theme Toggle**: Light/Dark mode support with persistent preference
- **Toast Notifications**: User-friendly feedback with auto-dismiss
- **Responsive Design**: Mobile-first approach with breakpoints for all devices
- **Conversation History**: Session-based chat history (not persisted)
- **Professional UI**: Navy blue color scheme with modern design

## 🚀 Quick Start

### Prerequisites

- Node.js 14+ and npm
- Backend API running on port 9090 (see `../back-end/README.md`)

### Installation

```bash
# Navigate to front-end directory
cd front-end

# Install dependencies
npm install

# Create .env file (already exists, modify if needed)
# API_URL=http://localhost:9090
# PORT=9091

# Start the development server
npm start
```

The application will be available at `http://localhost:9091`

## 📁 Project Structure

```
front-end/
├── server.js              # Express server entry point
├── package.json           # Node.js dependencies and scripts
├── .env                   # Environment configuration
├── .gitignore            # Git ignore rules
├── README.md             # This file
└── public/               # Static files
    ├── index.html        # Home page
    ├── chat.html         # Chat interface
    ├── about.html        # About page
    ├── contact.html      # Contact form
    ├── css/
    │   └── styles.css    # Main stylesheet (900+ lines)
    └── js/
        ├── main.js       # Common utilities, theme, toasts
        ├── chat.js       # Chat functionality
        └── contact.js    # Contact form handling
```

## 🎯 Pages Overview

### Home (`index.html`)
- Hero section with call-to-action
- Features showcase with icons
- How it works section
- Professional landing page design

### Chat (`chat.html`)
- Real-time chat interface with AI assistant
- Message history with timestamps
- Tool badges showing which tools were used
- Copy message functionality
- Auto-scrolling with manual scroll-down button
- Welcome message with tool overview

### About (`about.html`)
- Technology stack information
- Key features explanation
- System architecture overview
- Use cases and benefits

### Contact (`contact.html`)
- Contact form with validation
- FAQ section with expandable items
- Character counter for message field
- Success/error toast notifications

## 🛠️ Technology Stack

- **Runtime**: Node.js
- **Web Server**: Express.js
- **Frontend**: Vanilla JavaScript (no frameworks)
- **Styling**: Custom CSS with CSS variables
- **Icons**: Font Awesome 6.4.0
- **API Communication**: Fetch API

## ⚙️ Configuration

### Environment Variables (`.env`)

```env
API_URL=http://localhost:9090    # Backend API endpoint
PORT=9091                         # Frontend server port
NODE_ENV=development              # Environment mode
```

### JavaScript Configuration (`main.js`)

```javascript
const CONFIG = {
    API_URL: 'http://localhost:9090',  // Backend API
    TOAST_DURATION: 5000,               // Toast auto-dismiss time (ms)
    THEME_KEY: 'theme'                  // LocalStorage key for theme
};
```

## 📡 API Integration

The frontend communicates with the backend API:

### Health Check
```javascript
GET /health
Response: { status: "ok", agent_initialized: true, ... }
```

### Query Agent
```javascript
POST /query
Body: { question: "Your question here" }
Response: {
  question: "...",
  answer: "...",
  tools_used: ["google_search", "wikipedia"],
  timestamp: "2025-01-14T10:30:00Z"
}
```

## 🎨 Theming

### Light Mode (Default)
- Primary: Navy Blue (#1e3a8a)
- Background: White (#ffffff)
- Text: Dark Gray (#1f2937)

### Dark Mode
- Primary: Light Blue (#3b82f6)
- Background: Dark Navy (#0f172a)
- Text: Light Gray (#f1f5f9)

Theme preference is stored in `localStorage` and persists across sessions.

## 📱 Responsive Design

Breakpoints:
- **Mobile**: < 768px (single column, stacked navigation)
- **Tablet**: 768px - 1024px (adjusted spacing)
- **Desktop**: > 1024px (full layout)

## 🔧 Development

### Scripts

```bash
npm start          # Start development server
npm run dev        # Same as start (with nodemon if installed)
```

### Adding New Pages

1. Create HTML file in `public/`
2. Add navigation link in all existing pages
3. Create corresponding JS file if needed
4. Update styles in `styles.css`

### Modifying Styles

All styles are in `public/css/styles.css`:
- CSS variables at the top for easy theming
- Organized by sections (navigation, hero, chat, etc.)
- Mobile-first approach with media queries

## 🚨 Error Handling

- API connection errors show warning toast on chat page
- Form validation with real-time feedback
- Network errors display user-friendly messages
- Console logging for debugging

## 🔒 Security Considerations

- XSS prevention through `escapeHtml()` utility
- CORS configured on backend
- No sensitive data in localStorage
- Input validation on all forms

## 🧪 Testing

Manual testing checklist:
- [ ] Navigation works across all pages
- [ ] Theme toggle persists after reload
- [ ] Chat sends messages and receives responses
- [ ] Tools used are displayed correctly
- [ ] Toast notifications appear and dismiss
- [ ] Contact form validates and submits
- [ ] Responsive design works on mobile
- [ ] Conversation history persists in session
- [ ] Error messages display appropriately

## 📝 Future Enhancements

- [ ] Persistent conversation history (database)
- [ ] User authentication
- [ ] Conversation export functionality
- [ ] Markdown rendering in chat
- [ ] File upload for document retrieval
- [ ] Advanced search filters
- [ ] Analytics dashboard
- [ ] Internationalization (i18n)

## 🤝 Contributing

1. Follow existing code style and structure
2. Test on multiple browsers and devices
3. Update documentation for new features
4. Ensure accessibility standards (ARIA labels, keyboard navigation)

## 📄 License

This project is part of the Agentic RAG system. See main project repository for license information.

## 🆘 Troubleshooting

### Backend API Not Responding
- Verify backend is running on port 9090
- Check `.env` file has correct `API_URL`
- Confirm CORS is enabled on backend

### Theme Not Persisting
- Check browser localStorage is enabled
- Clear cache and reload
- Verify console for JavaScript errors

### Chat History Lost on Refresh
- This is expected behavior (session-based)
- For persistent history, backend integration needed

### Styling Issues
- Clear browser cache
- Check for CSS conflicts in browser DevTools
- Verify Font Awesome CDN is loading

## 📞 Support

For issues related to:
- **Frontend**: Check browser console and network tab
- **Backend**: See `../back-end/README.md`
- **API Integration**: Verify endpoint URLs and request/response formats

---

**Built with ❤️ for modern AI-powered research**
