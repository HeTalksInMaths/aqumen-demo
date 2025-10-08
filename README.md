# AI Code Review Mastery

An interactive game to test your code review skills by identifying conceptual errors in AI/ML code snippets.

## 🎯 Features

- **10 Code Challenges** spanning Beginner to Expert difficulty
- **Interactive Click Interface** - Click directly on problematic code segments
- **Real-time Scoring** with precision/recall metrics
- **Modern UI** built with React, Vite, and Tailwind CSS v4
- **Topics Include**: Transformers, RAG, LLM APIs, Fine-tuning, RLHF, Prompt Security

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and npm

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Visit `http://localhost:5173` in your browser.

### Build for Production

```bash
npm run build
```

The optimized files will be in the `dist/` folder.

## 📦 Deployment

### Deploy to Vercel (Recommended - FREE)

1. Push this code to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Import your GitHub repository
4. Vercel auto-detects Vite settings
5. Click "Deploy"

Your app will be live at `https://your-app.vercel.app`

### Deploy to GitHub Pages

```bash
# Build the app
npm run build

# Deploy dist folder to gh-pages branch
# (requires gh-pages package)
npm run deploy
```

## 🎮 How to Play

1. **Read the code** carefully - each snippet contains 1-3 conceptual errors
2. **Click on problematic segments** to identify errors
3. **Up to 3 clicks** before auto-submission
4. **Review results** - see what you caught and what you missed
5. **Learn from solutions** - understand the bugs and best practices

## 🔧 Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool
- **Tailwind CSS v4** - Styling (using new `@tailwindcss/postcss`)
- **Lucide React** - Icons
- **PostCSS** - CSS processing

## 🔮 Future Enhancements

- [ ] LLM-generated questions via API
- [ ] User authentication and score tracking
- [ ] Leaderboard
- [ ] Custom question sets
- [ ] Difficulty-based filtering
- [ ] Hints system

## 📄 License

MIT

## 🙏 Credits

Built with Claude Code and deployed on Aqumen.AI
