import React, { useState } from 'react';
import '../styles/Contact.css';

function Contact() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Form submission logic will be added later
    alert('Thank you for your message! We will get back to you soon.');
    setFormData({
      name: '',
      email: '',
      subject: '',
      message: ''
    });
  };

  return (
    <div className="contact">
      <div className="contact-hero">
        <h1 className="contact-title">Get in Touch</h1>
        <p className="contact-subtitle">
          We'd love to hear from you. Send us a message and we'll respond as soon as possible.
        </p>
      </div>

      <div className="contact-content">
        <div className="contact-info">
          <h2>Contact Information</h2>
          
          <div className="info-item">
            <div className="info-icon">📧</div>
            <div className="info-details">
              <h3>Email</h3>
              <p>support@agentquery.com</p>
            </div>
          </div>

          <div className="info-item">
            <div className="info-icon">💬</div>
            <div className="info-details">
              <h3>Live Chat</h3>
              <p>Available 24/7 for your queries</p>
            </div>
          </div>

          <div className="info-item">
            <div className="info-icon">🌐</div>
            <div className="info-details">
              <h3>Online Support</h3>
              <p>Monday - Friday: 9:00 AM - 6:00 PM EST</p>
            </div>
          </div>

          <div className="info-item">
            <div className="info-icon">📍</div>
            <div className="info-details">
              <h3>Location</h3>
              <p>Serving customers worldwide</p>
            </div>
          </div>

          <div className="social-links">
            <h3>Follow Us</h3>
            <div className="social-icons">
              <a href="#twitter" className="social-icon">Twitter</a>
              <a href="#linkedin" className="social-icon">LinkedIn</a>
              <a href="#github" className="social-icon">GitHub</a>
            </div>
          </div>
        </div>

        <div className="contact-form-container">
          <h2>Send Us a Message</h2>
          <form className="contact-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="name">Full Name *</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                placeholder="John Doe"
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">Email Address *</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                placeholder="john@example.com"
              />
            </div>

            <div className="form-group">
              <label htmlFor="subject">Subject *</label>
              <input
                type="text"
                id="subject"
                name="subject"
                value={formData.subject}
                onChange={handleChange}
                required
                placeholder="How can we help you?"
              />
            </div>

            <div className="form-group">
              <label htmlFor="message">Message *</label>
              <textarea
                id="message"
                name="message"
                value={formData.message}
                onChange={handleChange}
                required
                rows="6"
                placeholder="Tell us more about your inquiry..."
              ></textarea>
            </div>

            <button type="submit" className="submit-btn">
              Send Message
            </button>
          </form>
        </div>
      </div>

      <div className="faq-section">
        <h2>Frequently Asked Questions</h2>
        <div className="faq-grid">
          <div className="faq-item">
            <h3>How quickly will I receive a response?</h3>
            <p>
              We typically respond to all inquiries within 24 hours during business days.
            </p>
          </div>
          <div className="faq-item">
            <h3>Is Agent Query free to use?</h3>
            <p>
              Yes! Agent Query is currently free to use for all users.
            </p>
          </div>
          <div className="faq-item">
            <h3>What kind of questions can I ask?</h3>
            <p>
              You can ask any factual question. Our agent searches multiple sources 
              to provide comprehensive answers.
            </p>
          </div>
          <div className="faq-item">
            <h3>Do you offer API access?</h3>
            <p>
              Yes! Contact us for information about API access and integration options.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Contact;
