# Quick Start Guide

Get the frontend up and running in 3 simple steps!

## 🚀 Quick Start

```bash
# 1. Navigate to the frontend directory
cd frontend

# 2. Install dependencies (if not already done)
npm install

# 3. Start the development server
npm run dev
```

The application will automatically open in your browser at **http://localhost:3000**

## 🎯 First Time Setup

If this is your first time running the app:

1. **Onboarding Flow**: You'll see a welcome screen
2. **Set Preferences**: Configure your work hours and focus times
3. **Calendar Connection** (optional): Connect Google Calendar
4. **Dashboard**: Start managing tasks!

## 📱 What You'll See

### 1. Welcome & Onboarding
- Beautiful animated welcome screen
- Step-by-step preference setup
- Optional calendar integration

### 2. Main Dashboard
- AI assistant avatar (click to chat)
- Calendar view toggle (Day/Week/Month)
- Quick action buttons (Add Task, Goals, Settings)

### 3. AI Chat
- Click the floating sparkle button on the right
- Type tasks naturally: "Meeting tomorrow 2pm, 1 hour, work"
- AI parses and creates tasks automatically

### 4. Task Management
- Click "Tasks" button to see all tasks
- Switch between List and Kanban views
- Filter by category, status, and time
- Get AI suggestions for optimization

## 🎨 Try These Features

### Natural Language Task Input
```
"Team standup tomorrow at 9am, 30 minutes, work"
"Workout session, 1 hour, personal"
"Code review by Friday, 2 hours, work"
```

### Calendar Views
- **Day**: Hourly timeline for today
- **Week**: 7-day overview with time slots
- **Month**: Full calendar grid

### Task Organization
- **Categories**: Work (blue), Personal (purple), Focus (green)
- **Views**: List with filters or Kanban board
- **Statistics**: Track completion and progress

## 🛑 Stop the Server

Press `Ctrl + C` in the terminal

Or if running in background:
```bash
lsof -ti:3000 | xargs kill -9
```

## 🐛 Troubleshooting

### Port Already in Use
If port 3000 is occupied, Vite will automatically use the next available port.

### Dependencies Issues
```bash
# Clean install
rm -rf node_modules package-lock.json
npm install
```

### Build Issues
```bash
# Clear cache and rebuild
npm run build
```

## 📚 Next Steps

- See [README.md](README.md) for full documentation
- Check component files in `src/components/`
- Customize styles in `src/styles/globals.css`
- Connect to your backend API

## 💡 Tips

1. **Animations**: The app uses Framer Motion for smooth transitions
2. **Accessibility**: Full keyboard navigation support (Tab, Enter, Escape)
3. **Responsive**: Works on desktop and tablet (mobile optimization pending)
4. **Mock Data**: Currently uses sample data; ready for API integration

## 🔗 Useful Commands

```bash
# Development
npm run dev        # Start dev server

# Production
npm run build      # Build for production
npm run preview    # Preview production build

# Dependencies
npm install        # Install all dependencies
npm audit fix      # Fix security vulnerabilities
```

Enjoy building with the AI Scheduling Assistant! ✨
