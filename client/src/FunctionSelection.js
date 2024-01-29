import React from 'react';
import './FunctionSelection.css';
import {useNavigate} from "react-router-dom";

function FunctionSelection() {
  // 处理文件上传的函数
  const TimeSheetButtonClick = async () => {
      let navigate = useNavigate();
      try {
          // 发送请求到后端
          const response = await fetch('/api/get-payroll-data', {
              method: 'GET' // 或 'POST'，取决于你的后端实现
              // 如果需要，可以在这里添加 headers 或其他选项
          });

          if (response.ok) {
              // 请求成功，可以跳转到新页面
              console.log('Payroll data fetched successfully');
              navigate('/timesheet-dataupload');
          } else {
              // 处理错误情况
              console.error('Failed to fetch payroll data');
          }
      } catch (error) {
          console.error('Error during fetching payroll data:', error);
      }
  };

  return (
    <div className="timesheet-upload-container">
      <header className="header">
        Welcome to use
        <h1>Data automatic entry</h1>
      </header>
      <main className="main-content">
          <div className="button-grid">
            <button onClick={TimeSheetButtonClick} className="upload-button">
              TimeSheet DataUpload
            </button>
              <button className="upload-button">Button 2</button>
              <button className="upload-button">Button 3</button>
              <button className="upload-button">Button 4</button>
              <button className="upload-button">Button 5</button>
              <button className="upload-button">Button 6</button>
          </div>
      </main>
      <footer className="footer">
        QTC-automatic data entry
      </footer>
    </div>
  );
}

export default FunctionSelection;