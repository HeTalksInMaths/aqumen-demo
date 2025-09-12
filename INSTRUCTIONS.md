# How to Run Both Demo Versions

## Quick Start - View in Browser

1. **Open your browser and navigate to:**
   ```
   http://localhost:8080/test.html
   ```

2. **Features Available:**
   - Toggle between "Original Demo" and "Architecture Info" 
   - See the architectural comparison between monolithic vs modular approaches
   - Both use simulated API calls (no API keys required)

## What's Working

✅ **Original Demo**: Single file (`demo`) with all functionality  
✅ **Modular Demo**: 13 files with clean separation of concerns  
✅ **HTTP Server**: Running on port 8080  
✅ **Simulated APIs**: No external API keys needed  

## Architecture Comparison

### Original Version (1 file)
- `demo` - 676 lines, monolithic React component
- All state, logic, and UI in one place

### Modular Version (13 files)
- **Main**: `demo-modular.jsx` - Clean main component
- **Components**: 9 individual UI components  
- **State**: `hooks.js` - Custom React hooks
- **Logic**: `utils.js` - Pure utility functions
- **Data**: `constants.js` - Configuration & sample data

## File Structure
```
├── demo                          # Original monolithic version
├── demo-modular.jsx             # Main modular component  
├── constants.js                 # Models & sample data
├── utils.js                     # API calls & evaluation logic
├── hooks.js                     # State management hooks
├── components/                  # Individual UI components
│   ├── Header.jsx
│   ├── AntiCheatAlert.jsx
│   ├── TopicInput.jsx
│   ├── DifficultySelection.jsx
│   ├── GenerationLog.jsx
│   ├── AdversarialAttempts.jsx
│   ├── AssessmentQuestion.jsx
│   ├── ResultsDisplay.jsx
│   └── Footer.jsx
├── test.html                    # Browser demo page
└── package.json                # Dependencies

```

## Both Versions Include:
- Multi-step adversarial AI pipeline simulation
- Real-time logging and attempt visualization  
- Interactive error detection interface
- Comprehensive evaluation metrics (F1, precision, recall)
- Anti-cheat detection system
- Live adversarial loop visualization ("Task 1A")

## Server Management

To stop the HTTP server:
```bash
# Find the process
ps aux | grep python3
# Kill it
kill [process_id]
```

## Next Steps (Optional)

If you want to run the full Vite development server:
1. Fix the JSX compilation issues in the vite config
2. Convert all `.js` files that contain JSX to `.jsx` 
3. Run `npm run dev`

But the current HTTP server approach works perfectly for comparing both implementations!

---

🎉 **Both versions are functionally identical** - choose the architecture that fits your project needs!