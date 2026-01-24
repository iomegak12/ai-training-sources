import React from 'react';
import '../styles/About.css';

function About() {
  return (
    <div className="about">
      <div className="about-hero">
        <h1 className="about-title">About Agent Query</h1>
        <p className="about-subtitle">
          Empowering intelligent information discovery through AI
        </p>
      </div>

      <section className="about-section">
        <div className="about-content">
          <h2 className="content-title">Our Mission</h2>
          <p className="content-text">
            At Agent Query, we believe that access to accurate, comprehensive information 
            should be simple and intuitive. Our mission is to bridge the gap between complex 
            data sources and everyday users by leveraging cutting-edge AI technology to provide 
            intelligent, context-aware responses to any query.
          </p>
        </div>
      </section>

      <section className="about-section highlight">
        <div className="about-content">
          <h2 className="content-title">What We Do</h2>
          <p className="content-text">
            Agent Query is an advanced AI-powered search assistant that aggregates information 
            from multiple authoritative sources including Wikipedia, Google Search, academic 
            papers from Arxiv, and specialized knowledge bases. Our intelligent agent uses 
            state-of-the-art natural language processing to understand your questions and 
            deliver precise, relevant answers.
          </p>
        </div>
      </section>

      <section className="about-section">
        <div className="about-content">
          <h2 className="content-title">Our Technology</h2>
          <div className="tech-grid">
            <div className="tech-item">
              <h3>🤖 LangChain Agents</h3>
              <p>
                Advanced agent orchestration for intelligent decision-making and 
                tool selection based on your query context.
              </p>
            </div>
            <div className="tech-item">
              <h3>🧠 GPT-4 Intelligence</h3>
              <p>
                Powered by OpenAI's most advanced language model for natural, 
                accurate, and contextually relevant responses.
              </p>
            </div>
            <div className="tech-item">
              <h3>📊 Vector Search</h3>
              <p>
                FAISS-powered similarity search for lightning-fast retrieval 
                of relevant information from large knowledge bases.
              </p>
            </div>
            <div className="tech-item">
              <h3>🔗 Multi-Source Integration</h3>
              <p>
                Seamless integration with Wikipedia, Google Search, Arxiv, and 
                custom knowledge bases for comprehensive coverage.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="about-section">
        <div className="about-content">
          <h2 className="content-title">Why Choose Agent Query?</h2>
          <div className="benefits-list">
            <div className="benefit-item">
              <span className="benefit-icon">✓</span>
              <div>
                <h4>Accuracy & Reliability</h4>
                <p>
                  Our AI is trained to provide factual, verifiable information from 
                  trusted sources, ensuring you get reliable answers every time.
                </p>
              </div>
            </div>
            <div className="benefit-item">
              <span className="benefit-icon">✓</span>
              <div>
                <h4>Time-Saving Efficiency</h4>
                <p>
                  Instead of searching multiple websites, get consolidated answers 
                  from various sources in seconds.
                </p>
              </div>
            </div>
            <div className="benefit-item">
              <span className="benefit-icon">✓</span>
              <div>
                <h4>Intelligent Context Understanding</h4>
                <p>
                  Our agent understands nuance and context, providing answers that 
                  truly address what you're looking for.
                </p>
              </div>
            </div>
            <div className="benefit-item">
              <span className="benefit-icon">✓</span>
              <div>
                <h4>Continuous Learning</h4>
                <p>
                  Our system is constantly updated with the latest information and 
                  improvements to serve you better.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="about-section cta-section">
        <div className="about-content center">
          <h2 className="content-title">Experience the Difference</h2>
          <p className="content-text">
            Join thousands of users who trust Agent Query for their information needs.
          </p>
        </div>
      </section>
    </div>
  );
}

export default About;
