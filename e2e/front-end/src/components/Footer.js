import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/Footer.css';

function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-content">
          <div className="footer-section">
            <h3 className="footer-title">Agent Query</h3>
            <p className="footer-description">
              Intelligent AI-powered assistant leveraging multiple data sources 
              to provide accurate and comprehensive answers to your queries.
            </p>
          </div>

          <div className="footer-section">
            <h4 className="footer-heading">Quick Links</h4>
            <ul className="footer-links">
              <li><Link to="/">Home</Link></li>
              <li><Link to="/chat">Chat</Link></li>
              <li><Link to="/about">About Us</Link></li>
              <li><Link to="/contact">Contact</Link></li>
            </ul>
          </div>

          <div className="footer-section">
            <h4 className="footer-heading">Resources</h4>
            <ul className="footer-links">
              <li><a href="/docs" target="_blank" rel="noopener noreferrer">API Documentation</a></li>
              <li><a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">Swagger UI</a></li>
              <li><a href="#privacy">Privacy Policy</a></li>
              <li><a href="#terms">Terms of Service</a></li>
            </ul>
          </div>

          <div className="footer-section">
            <h4 className="footer-heading">Connect</h4>
            <p className="footer-text">
              Have questions or feedback? We'd love to hear from you.
            </p>
            <Link to="/contact" className="footer-cta">
              Get in Touch
            </Link>
          </div>
        </div>

        <div className="footer-bottom">
          <p className="footer-copyright">
            © {currentYear} Agent Query. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
