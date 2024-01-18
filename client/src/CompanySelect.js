// src/CompanySelect.js

import React, { useState, useEffect } from 'react';
import './CompanySelect.css'; // 确保有对应的样式文件

const CompanySelect = () => {
  const [companies, setCompanies] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchCompanies = async () => {
      setIsLoading(true);
      try {
        //  Flask 路由来获取公司列表
        const response = await fetch('/myob-callback');
        const data = await response.json();
        setCompanies(data);
        setIsLoading(false);
      } catch (error) {
        console.error('Error fetching companies:', error);
        setIsLoading(false);
      }
    };

    fetchCompanies();
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsLoading(true);

    //
    console.log('Selected Company:', selectedCompany);
    console.log('Username:', username);
    console.log('Password:', password);

    // 发送登录请求到您的后端
    // fetch('/api/login', { method: 'POST', body: JSON.stringify({ selectedCompany, username, password }), ... })
    //   .then(/* ... */)
    //   .finally(() => setIsLoading(false));
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="company-list-container">
      <form onSubmit={handleSubmit}>
        <label htmlFor="company-select">Select the company:</label>
        <select id="company-select" value={selectedCompany} onChange={(e) => setSelectedCompany(e.target.value)}>
          <option value="">Select the company</option>
          {companies.map((company) => (
            <option value={company.uid} key={company.uid}>
              {company.name} - {company.uid}
            </option>
          ))}
        </select>

        <div className="input-group">
          <label htmlFor="username">User name:</label>
          <input id="username" type="text" value={username} onChange={(e) => setUsername(e.target.value)} />
        </div>

        <div className="input-group">
          <label htmlFor="password">Password:</label>
          <input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>

        <div className="tip">Tip: If this company does not set a username and password. Please leave username and password blank</div>

        <button type="submit" className="button" disabled={isLoading}>
          {isLoading ? 'Loading...' : 'Log in'}
        </button>
      </form>
    </div>
  );
};

export default CompanySelect;