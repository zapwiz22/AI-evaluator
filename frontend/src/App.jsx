import React from 'react';
import FileUpload from './components/FileUpload';

function App() {
  return (
    <div style={{ textAlign: 'center', marginTop: '50px', fontFamily: 'sans-serif' }}>
      <h1>AI Evaluator Dashboard</h1>
      <FileUpload />
    </div>
  );
}

export default App;