# Aqumen Demo - Original vs Modular

This repository contains both the original monolithic React component and a modularized version of the Aqumen.ai Advanced Demo application.

## Files Overview

### Original Version
- `demo` - Original monolithic React component (676 lines)

### Modular Version
- `demo-modular.js` - Main component using modular architecture
- `constants.js` - Configuration constants and sample data
- `utils.js` - Utility functions for API calls, evaluation, and pipeline execution
- `hooks.js` - Custom React hooks for state management
- `components/` - Individual UI components:
  - `Header.js` - Application header with branding
  - `AntiCheatAlert.js` - Security alert component
  - `TopicInput.js` - Topic selection interface
  - `DifficultySelection.js` - Difficulty and subtopic selection
  - `GenerationLog.js` - Pipeline execution logging
  - `AdversarialAttempts.js` - Live adversarial loop visualization
  - `AssessmentQuestion.js` - Code assessment interface
  - `ResultsDisplay.js` - Performance metrics display
  - `Footer.js` - Application footer

### Support Files
- `package.json` - Dependencies and scripts
- `index.html` - Test page to compare both versions
- `test.js` - Basic tests to verify functionality
- `README.md` - This documentation

## Key Improvements in Modular Version

1. **Separation of Concerns**: Logic is separated into distinct modules
2. **Reusability**: Components can be used independently
3. **Maintainability**: Each file has a single responsibility
4. **Testability**: Individual components can be tested in isolation
5. **Readability**: Smaller, focused files are easier to understand

## Architecture

### State Management
- `usePipelineState()` - Main application state
- `useAdversarialAttempts()` - Logging and attempt tracking
- `useErrorClicks()` - Error interaction management
- `useAdversarialPipeline()` - Pipeline execution logic

### Utilities
- API simulation and timing
- Evaluation metrics calculations
- Anti-cheat detection
- Pipeline orchestration

### Components
Each UI component is self-contained with clear props interfaces, making the application more modular and maintainable.

## Running the Application

### Development
```bash
npm install
npm run dev
```

### Testing
```bash
npm test
```

### Browser Testing
Open `index.html` in a modern browser to compare both versions side-by-side.

## Functionality Verification

Both versions provide identical functionality:
- Multi-step adversarial pipeline execution
- Real-time logging and attempt visualization
- Interactive error detection interface
- Comprehensive evaluation metrics
- Anti-cheat detection system

The modular version maintains all features while providing better code organization and maintainability.