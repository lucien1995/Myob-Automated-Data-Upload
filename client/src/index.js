import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './index.css';
import HomePage from './HomePage';
import CompanySelect from './CompanySelect';
import reportWebVitals from './reportWebVitals';
import FunctionSelection from "./FunctionSelection";
import TimeSheetUpload from "./FunctionSelection";
import TimesheetDataUpload from "./TimesheetDataUpload";

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
   <BrowserRouter>
      <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/company-select" element={<CompanySelect />} />
          <Route path="/function-selection" element={<FunctionSelection />} />
          <Route path="/timesheet-dataupload" element={<TimesheetDataUpload />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function            <Route path="/" element={<HomePage />} />
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
