# Agent Query - Frontend

A modern React-based web application for interacting with the Agent Query API, featuring an intuitive chat interface and professional design.

## Features

- 🎨 **Modern UI**: Clean, professional design with sky blue color scheme
- 📱 **Responsive**: Mobile-friendly and fully responsive layout
- 🧭 **Multi-Page**: Home, Chat, About, and Contact pages with smooth navigation
- 💬 **Chat Interface**: Interactive chat UI for querying the AI agent
- ⚡ **Fast**: Optimized with Webpack for quick load times
- 🎯 **Simple**: Pure JavaScript (no TypeScript), vanilla CSS (no frameworks)

## Technology Stack

- **React 18** - UI library
- **React Router** - Client-side routing
- **Webpack 5** - Module bundler
- **Babel** - JavaScript compiler
- **Pure JavaScript** - No TypeScript
- **Vanilla CSS** - No CSS frameworks

## Prerequisites

- Node.js 14+ and npm

## Installation

1. **Navigate to front-end directory**
   ```bash
   cd front-end
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

## Running the Application

### Development Mode

```bash
npm start
```

The app will automatically open at `http://localhost:8002`

### Development Mode (without auto-open)

```bash
npm run dev
```

### Production Build

```bash
npm run build
```

The optimized build will be in the `dist/` folder.

## Project Structure

```
front-end/
├── public/
│   └── index.html           # HTML template
├── src/
│   ├── components/
│   │   ├── Navigation.js    # Navigation bar component
│   │   └── Footer.js        # Footer component
│   ├── pages/
│   │   ├── Home.js          # Home page
│   │   ├── Chat.js          # Chat interface page
│   │   ├── About.js         # About page
│   │   └── Contact.js       # Contact page
│   ├── styles/
│   │   ├── global.css       # Global styles and variables
│   │   ├── App.css          # App layout styles
│   │   ├── Navigation.css   # Navigation styles
│   │   ├── Footer.css       # Footer styles
│   │   ├── Home.css         # Home page styles
│   │   ├── Chat.css         # Chat page styles
│   │   ├── About.css        # About page styles
│   │   └── Contact.css      # Contact page styles
│   ├── App.js               # Main app component with routing
│   └── index.js             # Entry point
├── webpack.config.js        # Webpack configuration
├── .babelrc                 # Babel configuration
├── package.json             # Dependencies and scripts
└── README.md                # This file
```

## Pages

### Home (`/`)
- Hero section with call-to-action
- Features showcase
- Benefits overview

### Chat (`/chat`)
- Interactive chat interface
- Real-time messaging (to be connected to API)
- Message history display

### About (`/about`)
- Company mission and vision
- Technology overview
- Benefits and features

### Contact (`/contact`)
- Contact form
- Contact information
- FAQ section

## Design System

### Color Palette

```css
Primary: #0EA5E9 (Sky Blue)
Primary Dark: #0284C7
Primary Light: #38BDF8
White: #FFFFFF
Gray shades: #F9FAFB to #111827
```

### Typography

- Font: Inter (Google Fonts)
- Responsive font sizes
- Consistent spacing

### Components

- Reusable button styles
- Consistent card layouts
- Responsive grid systems

## Development Guidelines

### Adding a New Page

1. Create a new component in `src/pages/`
2. Create corresponding CSS file in `src/styles/`
3. Add route in `src/App.js`
4. Add navigation link in `src/components/Navigation.js`

### Styling Conventions

- Use CSS variables from `global.css`
- Follow mobile-first responsive design
- Maintain consistent spacing using spacing variables
- Use semantic class names

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance

- Code splitting with Webpack
- Lazy loading for routes
- Optimized CSS bundling
- Production build minification

## Future Enhancements

- [ ] Connect chat to backend API
- [ ] Add loading states
- [ ] Implement chat history
- [ ] Add error handling
- [ ] Add animations
- [ ] Implement dark mode
- [ ] Add internationalization

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please visit the Contact page or open an issue in the repository.
