import React, { useState, useEffect } from 'react';

function App() {
  const [status, setStatus] = useState('loading');
  const [data, setData] = useState(null);

  useEffect(() => {
    // Тест API соединения
    fetch('http://localhost:8001/api/stats')
      .then(res => res.json())
      .then(data => {
        setData(data);
        setStatus('success');
      })
      .catch(err => {
        console.error('API Error:', err);
        setStatus('error');
      });
  }, []);

  return (
    <div style={{ 
      padding: '20px', 
      fontFamily: 'Arial, sans-serif',
      minHeight: '100vh',
      backgroundColor: '#f5f5f5'
    }}>
      <div style={{
        maxWidth: '800px',
        margin: '0 auto',
        backgroundColor: 'white',
        padding: '20px',
        borderRadius: '8px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
      }}>
        <h1 style={{ 
          color: '#333', 
          textAlign: 'center',
          marginBottom: '30px'
        }}>
          Email Intelligence Collector
        </h1>
        
        <div style={{
          padding: '20px',
          backgroundColor: status === 'success' ? '#e6ffe6' : status === 'error' ? '#ffe6e6' : '#fff3cd',
          border: `1px solid ${status === 'success' ? '#99ff99' : status === 'error' ? '#ff9999' : '#ffeaa7'}`,
          borderRadius: '4px',
          marginBottom: '20px'
        }}>
          <h3>Статус системы:</h3>
          <ul>
            <li>✅ React: работает</li>
            <li>✅ Docker: запущен</li>
            <li>✅ Vite: работает</li>
            <li>{status === 'success' ? '✅' : status === 'error' ? '❌' : '⏳'} API: {status}</li>
          </ul>
        </div>

        {status === 'success' && data && (
          <div style={{
            padding: '15px',
            backgroundColor: '#f8f9fa',
            borderRadius: '4px'
          }}>
            <h3>Данные API:</h3>
            <p>Профилей в базе: {data.total_profiles}</p>
            <p>Выполнено поисков: {data.total_searches}</p>
            <p>Последних поисков: {data.recent_searches?.length || 0}</p>
          </div>
        )}

        {status === 'error' && (
          <div style={{
            padding: '15px',
            backgroundColor: '#ffe6e6',
            border: '1px solid #ff9999',
            borderRadius: '4px'
          }}>
            <h3>Ошибка подключения к API</h3>
            <p>Проверьте, что backend запущен на порту 8001</p>
          </div>
        )}

        <div style={{ marginTop: '30px', textAlign: 'center' }}>
          <p style={{ color: '#666' }}>
            🎉 React приложение успешно загружено и отображается!
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
