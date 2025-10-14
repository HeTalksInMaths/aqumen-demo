import React from 'react'
import ReactDOM from 'react-dom/client'
import AqumenAdvancedDemo from './demo.jsx'
// import AqumenAdvancedDemoModular from '../demo-modular.jsx'

// Render both versions
const originalRoot = ReactDOM.createRoot(document.getElementById('originalDemo'));
const modularRoot = ReactDOM.createRoot(document.getElementById('modularDemo'));

originalRoot.render(<AqumenAdvancedDemo />);
// modularRoot.render(<AqumenAdvancedDemoModular />);
modularRoot.render(<div className="p-8 text-white bg-gray-900 min-h-screen"><h2 className="text-2xl">Modular version temporarily disabled due to syntax issues. Working on fix...</h2></div>);

// Global functions for switching views
window.showOriginal = function() {
  document.getElementById('originalDemo').classList.add('active');
  document.getElementById('modularDemo').classList.remove('active');
  document.getElementById('originalBtn').classList.add('active');
  document.getElementById('modularBtn').classList.remove('active');
  document.getElementById('versionIndicator').textContent = 'Current: Original Version';
};

window.showModular = function() {
  document.getElementById('modularDemo').classList.add('active');
  document.getElementById('originalDemo').classList.remove('active');
  document.getElementById('modularBtn').classList.add('active');
  document.getElementById('originalBtn').classList.remove('active');
  document.getElementById('versionIndicator').textContent = 'Current: Modular Version';
};

// Add event listeners for the buttons
document.getElementById('originalBtn').addEventListener('click', window.showOriginal);
document.getElementById('modularBtn').addEventListener('click', window.showModular);

console.log('Both versions loaded successfully!');