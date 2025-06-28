import React from 'react';

function App() {
  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#f0f0f0',
      padding: '20px',
      fontFamily: 'Arial, sans-serif'
    }}>
      <div style={{
        maxWidth: '800px',
        margin: '0 auto',
        backgroundColor: 'white',
        padding: '20px',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <h1 style={{ 
          color: '#333', 
          textAlign: 'center',
          marginBottom: '20px'
        }}>
          Email Intelligence Collector - Debug Mode
        </h1>
        
        <div style={{
          backgroundColor: '#e8f5e8',
          border: '1px solid #4caf50',
          padding: '15px',
          borderRadius: '4px',
          marginBottom: '20px'
        }}>
          <p>✅ React is working correctly!</p>
          <p>✅ JavaScript is executing</p>
          <p>✅ Component is rendering</p>
        </div>

        <div style={{
          backgroundColor: '#fff3cd',
          border: '1px solid #ffc107',
          padding: '15px',
          borderRadius: '4px',
          marginBottom: '20px'
        }}>
          <h3>Debug Information:</h3>
          <p><strong>Current Time:</strong> {new Date().toLocaleString()}</p>
          <p><strong>User Agent:</strong> {navigator.userAgent.substring(0, 50)}...</p>
          <p><strong>Window Size:</strong> {window.innerWidth} x {window.innerHeight}</p>
        </div>

        <div style={{
          backgroundColor: '#d1ecf1',
          border: '1px solid #17a2b8',
          padding: '15px',
          borderRadius: '4px'
        }}>
          <h3>Next Steps:</h3>
          <ol>
            <li>If you can see this page, React is working correctly</li>
            <li>The issue might be with the UI components or API calls</li>
            <li>Check the browser console for any errors</li>
            <li>Try refreshing the page</li>
          </ol>
        </div>
      </div>
    </div>
  );
}

export default App;
