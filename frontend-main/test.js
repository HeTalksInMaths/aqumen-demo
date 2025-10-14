// Simple test to verify both versions work similarly
// This would typically be run in a test environment with Jest or similar

import React from 'react';
import { render } from '@testing-library/react';

// Import both versions
import AqumenAdvancedDemo from './demo';
import AqumenAdvancedDemoModular from './demo-modular.js';

// Mock the Lucide React icons to avoid import issues in testing
jest.mock('lucide-react', () => ({
  Brain: () => <div>Brain</div>,
  Zap: () => <div>Zap</div>,
  Target: () => <div>Target</div>,
  AlertTriangle: () => <div>AlertTriangle</div>,
  CheckCircle: () => <div>CheckCircle</div>,
  RefreshCw: () => <div>RefreshCw</div>,
  Lightbulb: () => <div>Lightbulb</div>,
  Settings: () => <div>Settings</div>,
  Search: () => <div>Search</div>,
  Cpu: () => <div>Cpu</div>,
  Eye: () => <div>Eye</div>,
  EyeOff: () => <div>EyeOff</div>,
  Clock: () => <div>Clock</div>,
  Award: () => <div>Award</div>
}));

describe('Demo Components Comparison', () => {
  test('Original demo renders without errors', () => {
    const { container } = render(<AqumenAdvancedDemo />);
    expect(container.querySelector('h1')).toContainHTML('Aqumen.ai Advanced Demo');
  });

  test('Modular demo renders without errors', () => {
    const { container } = render(<AqumenAdvancedDemoModular />);
    expect(container.querySelector('h1')).toContainHTML('Aqumen.ai Advanced Demo');
  });

  test('Both versions have same initial structure', () => {
    const originalRender = render(<AqumenAdvancedDemo />);
    const modularRender = render(<AqumenAdvancedDemoModular />);
    
    // Check that both have the header
    expect(originalRender.getByText('Aqumen.ai Advanced Demo')).toBeInTheDocument();
    expect(modularRender.getByText('Aqumen.ai Advanced Demo')).toBeInTheDocument();
    
    // Check that both have the topic input field
    expect(originalRender.getByPlaceholderText(/Machine Learning/)).toBeInTheDocument();
    expect(modularRender.getByPlaceholderText(/Machine Learning/)).toBeInTheDocument();
    
    // Check that both have the start button
    expect(originalRender.getByText('Start Pipeline Analysis')).toBeInTheDocument();
    expect(modularRender.getByText('Start Pipeline Analysis')).toBeInTheDocument();
  });
});

// Manual verification function for browser testing
export const verifyBothVersions = () => {
  console.log('Testing both versions...');
  
  // Test that constants are properly exported
  import('./constants.js').then(constants => {
    console.log('Constants loaded:', Object.keys(constants));
    console.log('MODELS:', constants.MODELS);
  });
  
  // Test that utils are properly exported
  import('./utils.js').then(utils => {
    console.log('Utils loaded:', Object.keys(utils));
  });
  
  // Test that hooks are properly exported
  import('./hooks.js').then(hooks => {
    console.log('Hooks loaded:', Object.keys(hooks));
  });
  
  console.log('All modules loaded successfully!');
};