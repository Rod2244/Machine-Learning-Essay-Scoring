import React from "react";
import "../LP-css/home.css";
import "../LP-css/about-us.css";
import TopBar from "../LP-components/top-bar";
import aboutUsBgImage from "../../About-us.png";
import studentsImage from "../../students.png";

export default function AboutUs({ onNavigate }) {
  return (
    <div className="home">
      <TopBar onNavigate={onNavigate} currentPage="about" />

      {/* ABOUT US HERO SECTION */}
      <section className="hero" id="about">
        <div className="hero-overlay" />
        
        {/* ABOUT US BACKGROUND IMAGE */}
        <div className="hero-decoration">
          <img src={aboutUsBgImage} alt="About Us Background" className="hero-bg-image" />
        </div>
        
        <div className="hero-content">
          <h1 className="delight-title">ABOUT US</h1>
          <p>
            Learn more about our team and the Essay Scoring System we've developed.
          </p>
        </div>
      </section>

      {/* ABOUT US CONTENT */}
      <section className="section light">
        <div className="container">
          <div className="about-content">
            <div className="about-section">
              <h3>🔹 Who We Are</h3>
              <p>
                We are students developing a Machine Learning-based Essay Scoring System designed to evaluate written responses automatically. This project was created as part of our academic requirement to explore the capabilities of artificial intelligence in education.
              </p>
            </div>

            <div className="about-section">
              <h3>🔹 What Our System Does</h3>
              <p>
                Our system allows users to input a question, write an essay, and set specific evaluation criteria. Using machine learning techniques, the system analyzes the essay and provides a score based on the given standards.
              </p>
              <p>
                Our project focuses on structured evaluation and scoring rather than generating answers, making it a practical tool for learning and assessment.
              </p>
            </div>

            <div className="about-section">
              <h3>🔹 Our Goal</h3>
              <p>
                Our goal is to develop a system that helps automate essay checking while promoting consistency and efficiency in grading. We aim to demonstrate how machine learning can assist educators in evaluating written work.
              </p>
            </div>

            <div className="about-section">
              <h3>🔹 Our Vision</h3>
              <p>
                We envision a future where AI-powered tools can support education by simplifying tasks such as essay evaluation, while still encouraging students to think critically and express their ideas clearly.
              </p>
            </div>

            <div className="about-section">
              <h3>🔹 Developers</h3>
              <div className="developers-list">
                <p>Rod Angelo Ignacio</p>
                <p>Ern Francis Natividad</p>
                <p>John Zander Remillete</p>
                <p>Claire Tuble</p>
                <p>Ashley Nicole Villanueva</p>
                <p>Maria Victoria Jean Zambales</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="cta about-us-cta">
        <div className="cta-content">
          <div className="cta-text">
            <h2>Ready to evaluate your essay?</h2>
            <button className="secondary-btn" onClick={() => window.dispatchEvent(new CustomEvent('showMainApp'))}>Try the System Now</button>
          </div>
          <div className="cta-image">
            <img src={studentsImage} alt="Students" className="students-image" />
          </div>
        </div>
      </section>
    </div>
  );
}