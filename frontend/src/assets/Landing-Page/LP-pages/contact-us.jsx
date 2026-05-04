import React, { useEffect } from "react";
import "../LP-css/home.css";
import "../LP-css/contact-us.css";
import TopBar from "../LP-components/top-bar";

export default function ContactUs({ onNavigate }) {
  // Force light mode on landing page
  useEffect(() => {
    // Remove dark-mode class if it exists
    document.documentElement.classList.remove('dark-mode');
  }, []);
  return (
    <div className="home">
      <TopBar onNavigate={onNavigate} currentPage="contact" />

      {/* CONTACT CONTENT */}
      <section className="section light">
        <div className="container">
          <div className="contact-layout">
            {/* LEFT SIDE - Get in Touch and Contact Information */}
            <div className="contact-left">
              <div className="about-section">
                <h2 className="get-in-touch-title">Get in Touch</h2>
                <p>
                  Have questions, feedback, or suggestions about our Essay Scoring System? We'd love to hear from you. Feel free to reach out to our team using the information below.
                </p>
              </div>
              
              <div className="about-section">
                <h3>Contact Information</h3>
                <div className="contact-details">
                  <p><strong>✉️ Email:</strong> yourproject@email.com</p>
                  <p><strong>📍 Location:</strong> Zamboanga City, Philippines</p>
                </div>
              </div>
            </div>

            {/* RIGHT SIDE - Send Us a Message Form */}
            <div className="contact-right">
              <div className="contact-form-box">
                <h3>Send Us a Message</h3>
                <div className="contact-form">
                  <form onSubmit={(e) => { e.preventDefault(); alert('Thank you for your message! We will get back to you soon.'); }}>
                    <div className="form-group">
                      <label htmlFor="name">Name:</label>
                      <input type="text" id="name" name="name" required />
                    </div>
                    <div className="form-group">
                      <label htmlFor="email">Email:</label>
                      <input type="email" id="email" name="email" required />
                    </div>
                    <div className="form-group">
                      <label htmlFor="subject">Subject:</label>
                      <input type="text" id="subject" name="subject" required />
                    </div>
                    <div className="form-group">
                      <label htmlFor="message">Message:</label>
                      <textarea id="message" name="message" rows="5" required></textarea>
                    </div>
                    <button type="submit" className="primary-btn">Send Message</button>
                  </form>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}