import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/Home.css';

function Home() {
  return (
    <div className="home">
      <section className="hero">
        <div className="hero-content">
          <h1 className="hero-title">
            Welcome to <span className="highlight">Agent Query</span>
          </h1>
          <p className="hero-subtitle">
            Your Intelligent AI Assistant
          </p>
          <p className="hero-description">
            Harness the power of multiple data sources including Wikipedia, Google Search, 
            Arxiv, and advanced RAG technology to get accurate, comprehensive answers to your questions.
          </p>
          <div className="hero-buttons">
            <Link to="/chat" className="btn btn-primary">
              Start Chatting
            </Link>
            <Link to="/about" className="btn btn-secondary">
              Learn More
            </Link>
          </div>
        </div>
      </section>

      <section className="features">
        <div className="section-header">
          <h2 className="section-title">Powerful Features</h2>
          <p className="section-subtitle">
            Everything you need for intelligent information retrieval
          </p>
        </div>

        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🔍</div>
            <h3 className="feature-title">Multi-Source Search</h3>
            <p className="feature-description">
              Access information from Wikipedia, Google Search, and academic papers 
              from Arxiv all in one place.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🧠</div>
            <h3 className="feature-title">AI-Powered Intelligence</h3>
            <p className="feature-description">
              Leverage advanced LangChain agents and GPT-4 technology for 
              intelligent, context-aware responses.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">⚡</div>
            <h3 className="feature-title">Fast & Reliable</h3>
            <p className="feature-description">
              Get quick, accurate answers with our optimized API and 
              high-performance retrieval system.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">📚</div>
            <h3 className="feature-title">RAG Technology</h3>
            <p className="feature-description">
              Retrieval-Augmented Generation ensures responses are grounded 
              in factual, up-to-date information.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">💬</div>
            <h3 className="feature-title">Natural Conversations</h3>
            <p className="feature-description">
              Engage in natural, flowing conversations with our intelligent 
              chat interface.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🔒</div>
            <h3 className="feature-title">Secure & Private</h3>
            <p className="feature-description">
              Your queries and data are handled with the highest standards 
              of security and privacy.
            </p>
          </div>
        </div>
      </section>

      <section className="cta-section">
        <div className="cta-content">
          <h2 className="cta-title">Ready to Get Started?</h2>
          <p className="cta-description">
            Experience the power of AI-driven information retrieval today.
          </p>
          <Link to="/chat" className="btn btn-primary btn-large">
            Try Agent Query Now
          </Link>
        </div>
      </section>
    </div>
  );
}

export default Home;
