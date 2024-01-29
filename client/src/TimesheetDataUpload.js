import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import './TimesheetDataUpload.css'; // 确保CSS文件名与此处匹配

const TimesheetDataUpload = () => {
  const [file, setFile] = useState(null);
  const [previewData, setPreviewData] = useState(null);
  const [uploading, setUploading] = useState(false);

  const onDrop = useCallback(acceptedFiles => {
    const file = acceptedFiles[0];
    if (file) {
      // 仅当文件为Excel文件时，设置文件
      console.log('File accepted:', file);
      setFile(file);
      setUploading(false); // 重置上传状态
      // 可以在这里添加更多文件验证逻辑
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
    accept: '.xls,.xlsx'
  });

  const handleUpload = async () => {    //////////////////////////////////////从这里继续
    if (!file) return;

    setUploading(true); // 设置上传状态为true
    console.log('Uploading file:', file);
    // TODO: 实现文件上传到后端的逻辑
    // 例如使用 fetch API 或者其他库来发送文件到后端

    const formData = new FormData();
    formData.append('file', file);


     try {
    // 发送请求到后端上传接口
    const response = await fetch('/timesheet-upload', {
      method: 'POST',
      body: formData,
      // 不要设置 'Content-Type' 头，浏览器会自动设置
      // 并且包含 boundary 参数（multipart/form-data; boundary=----WebKitFormBoundary...）
    });

    // 检查响应是否成功
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // 获取后端返回的数据，可能包含文件处理结果
    const result = await response.json();
    console.log('Upload result:', result);
    setPreviewData(result.previewData); // 假设后端返回了预览数据
  } catch (error) {
    console.error('Upload failed', error);
  } finally {
    setUploading(false); // 重置上传状态
  }

    // 模拟文件上传和处理
    setTimeout(() => {
      // 假设后端返回了预览数据
      const mockPreviewData = 'Data from file'; // 替换为实际预览数据
      setPreviewData(mockPreviewData);
      setUploading(false); // 重置上传状态
    }, 2000);
  };

  const handleSubmitUpload = () => {
    console.log('Confirming Submitting...');
    // Here you would handle the final upload confirmation
  };

  // 渲染拖拽区域和上传按钮
 return (
    <div className="upload-page-container">
      <div className="welcome-section">
        <h2>Welcome to use </h2>
           <h1> Data Automatic Entry</h1>
        <hr />
      </div>
      <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
        <input {...getInputProps()} />
        {
          file
          ? <p>{file.name}</p> // Display the file name if a file is selected
          : ( // Otherwise, show the drag and drop message
              <>
                <p>Please drag or click the area to select the file</p>
                <p>Only one Excel file can be accepted</p>
              </>
            )
        }
      </div>
      <button className="upload-button" onClick={handleUpload} disabled={uploading}>
        {uploading ? 'Uploading...' : 'Select'}
      </button>
      {previewData && (
        <div className="preview-section">
          <span className="preview-label">Preview:</span>
          <div className="preview-content">{previewData}</div>
          <button className="confirm-button" onClick={handleSubmitUpload}>Confirm upload</button>
        </div>
      )}
    </div>
  );
};

export default TimesheetDataUpload;