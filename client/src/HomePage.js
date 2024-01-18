// src/HomePage.js

import React from 'react';
import './HomePage.css';

const HomePage = () => {
  return (
    <div className="home-container">
      <header className="home-header">
        <h1>Welcome to use</h1>
        <h2>Data automatic entry</h2>
        <hr />
      </header>
      <main className="home-content">
        <button onClick={() => window.location.href = 'http://localhost:5000/get-auth-code'}>
          Get Access Token
        </button>
        <p>Click the 'Get Access Token' button to obtain MYOB permissions.</p>
      </main>
      <footer className="home-footer">
        <p>QTC-automatic data entry</p>
      </footer>
    </div>
  );
};

export default HomePage;