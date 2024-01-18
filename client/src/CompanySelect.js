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

  const handleSubmit = async (e) => {
  e.preventDefault();
  setIsLoading(true);

  try {
    const response = await fetch('/CompanyDetail', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // 如果您使用 session 或 token，可能还需要添加授权头部
        // 'Authorization': 'Bearer YOUR_TOKEN_HERE',
      },
      body: JSON.stringify({
        selectedCompany,
        username,
        password
      }),
    });

    const data = await response.json();
    if (response.ok) {
      // 处理成功响应
      console.log('Success:', data);
      // 可能的操作：跳转到详情页、显示成功信息等
    } else {
      // 处理错误响应
      console.error('Login failed:', data);
      // 显示错误信息等
    }
  } catch (error) {
    console.error('Request failed', error);
    // 显示错误信息等
  } finally {
    setIsLoading(false);
  }
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