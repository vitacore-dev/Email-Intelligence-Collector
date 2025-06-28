import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App-debug.jsx'

console.log('Debug main.jsx loaded');

const rootElement = document.getElementById('root');
console.log('Root element found:', rootElement);

if (rootElement) {
  const root = createRoot(rootElement);
  console.log('React root created');
  
  root.render(
    <StrictMode>
      <App />
    </StrictMode>
  );
  console.log('App rendered');
} else {
  console.error('Root element not found!');
}
