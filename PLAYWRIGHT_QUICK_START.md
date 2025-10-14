# ✅ Playwright Setup Complete!

## 🎯 Quick Reference

### From `frontend-main-branch` directory:

```bash
cd /Users/hetalksinmaths/adversarial\ demo/frontend-main-branch
```

## 📸 Taking Screenshots

```bash
# Take full-page screenshots
npm run test:screenshot

# Run all tests and capture screenshots
npm run test:e2e

# View screenshots
npm run test:report
```

## 🐛 Interactive Debugging

```bash
# Open Playwright Inspector (pause, step through, inspect)
npm run test:e2e:debug

# Run tests with browser visible
npm run test:e2e:headed

# Interactive UI mode
npm run test:e2e:ui

# Record your clicks and generate test code
npm run test:codegen
```

## 📝 Available Test Files

### 1. **dev-student-screenshots.spec.ts** (Basic)
- Student Mode screenshot
- Dev Mode screenshot
- Quick visual checks

### 2. **debug-helper.spec.ts** (Advanced) ⭐
- Full-page screenshots at different viewports
- Click flow testing
- Element inspection (lists all buttons, inputs, headings)
- Console error detection
- Network request monitoring
- Interactive pause mode

## 🎬 Common Debugging Workflows

### Workflow 1: "I want to see the current UI"
```bash
npm run test:e2e -- tests/e2e/debug-helper.spec.ts -g "full-page screenshot"
npm run test:report  # Opens browser with screenshots
```

### Workflow 2: "Let me click around manually"
```bash
npm run test:e2e:debug -- tests/e2e/debug-helper.spec.ts -g "pause for manual"
# Playwright Inspector opens → you can interact with the page
```

### Workflow 3: "What buttons/elements are on the page?"
```bash
npm run test:e2e -- tests/e2e/debug-helper.spec.ts -g "inspect element locators"
# Check terminal output for full list
```

### Workflow 4: "Test different screen sizes"
```bash
npm run test:e2e -- tests/e2e/debug-helper.spec.ts -g "viewport"
npm run test:report  # See desktop, tablet, mobile screenshots
```

### Workflow 5: "Are there any JavaScript errors?"
```bash
npm run test:e2e -- tests/e2e/debug-helper.spec.ts -g "console errors"
```

### Workflow 6: "Record a new test for me"
```bash
npm run test:codegen
# Browser opens → click around → test code is generated
```

## 🚀 How It Works

1. **Auto-starts dev server**: Playwright runs `npm run dev` automatically
2. **Waits for server**: Ensures `http://localhost:5173` is ready
3. **Runs tests**: Opens Chromium and executes tests
4. **Captures artifacts**: Screenshots, videos, traces saved on failure
5. **Generates report**: HTML report with all results

## 📁 Where Files Are Saved

```
frontend-main-branch/
├── test-results/          # Screenshots, videos, traces
├── playwright-report/     # HTML report (open with npm run test:report)
└── tests/e2e/
    ├── dev-student-screenshots.spec.ts  # Basic tests
    ├── debug-helper.spec.ts             # Advanced debugging
    └── README.md                        # Full documentation
```

## 🔧 Configuration

See `playwright.config.ts` in project root:
- **Timeout**: 30 seconds per test
- **Retries**: 0 locally, 2 in CI
- **baseURL**: http://localhost:5173
- **Backend API**: http://localhost:8000 (via VITE_API_URL)

## 💡 Pro Tips

1. **Always use `--debug` when developing tests**
   ```bash
   npm run test:e2e:debug
   ```

2. **View the HTML report after every run**
   ```bash
   npm run test:report
   ```

3. **Use codegen to create new tests quickly**
   ```bash
   npm run test:codegen
   ```

4. **Run specific test by name**
   ```bash
   npm run test:e2e -- -g "click through student mode"
   ```

5. **Check screenshots even when tests pass**
   ```bash
   ls -la test-results/
   ```

## 🎓 For Claude Code

When I need to debug the React frontend:

1. **Take a screenshot**:
   ```bash
   npm run test:screenshot
   ```

2. **See what elements exist**:
   ```bash
   npm run test:e2e -- tests/e2e/debug-helper.spec.ts -g "inspect element"
   ```

3. **Check for errors**:
   ```bash
   npm run test:e2e -- tests/e2e/debug-helper.spec.ts -g "console errors"
   ```

4. **Interactive debugging**:
   ```bash
   npm run test:e2e:debug -- tests/e2e/debug-helper.spec.ts -g "pause"
   ```

## ⚡ Next Steps

- [ ] Add tests for live pipeline streaming
- [ ] Add tests for topic input and generation flow
- [ ] Create tests for error clicking interactions
- [ ] Add API mocking for offline testing
- [ ] Integrate into CI/CD pipeline

## 📚 Full Documentation

See `tests/e2e/README.md` for comprehensive guide.

---

**Status**: ✅ **READY TO USE**

Run `npm run test:e2e` to verify everything works!
