# AI Scheduling Assistant - Frontend

A beautiful, modern React frontend for the AI Scheduling Assistant application, designed in Figma and exported as production-ready code.

## 🎨 Overview

This is a complete UI implementation featuring:
- **Glassmorphism Design**: Modern glass-effect aesthetic with soft pastel colors
- **AI Chat Interface**: Natural language task input with conversational AI
- **Calendar Management**: Day/Week/Month views with Google Calendar integration
- **Task Management**: Comprehensive task organization with multiple views (List/Kanban)
- **Onboarding Flow**: Smooth multi-step user onboarding experience
- **Accessibility First**: WCAG 2.0 compliant with full keyboard navigation

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```

3. **Open your browser:**
   - Navigate to the URL shown in the terminal (typically `http://localhost:5173`)

### Build for Production

```bash
npm run build
```

The optimized production files will be in the `dist/` directory.

## 🏗️ Tech Stack

- **React 18.3.1** - UI framework
- **TypeScript** - Type safety
- **Vite 6.3.5** - Build tool and dev server
- **Tailwind CSS v4** - Utility-first styling
- **Framer Motion** - Smooth animations and transitions
- **Radix UI** - Accessible component primitives
- **Lucide React** - Beautiful icon library
- **React Hook Form** - Form handling

## 📦 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Dashboard.tsx         # Main dashboard view
│   │   ├── OnboardingFlow.tsx    # Multi-step onboarding
│   │   ├── AIPanel.tsx           # AI chat interface
│   │   ├── TaskManagement.tsx    # Task organization views
│   │   ├── CalendarView.tsx      # Calendar display
│   │   ├── TaskForm.tsx          # Task creation/editing
│   │   ├── MonthlyGoals.tsx      # Goal tracking
│   │   ├── GoogleCalendarFlow.tsx # OAuth flow
│   │   └── ui/                   # Reusable UI components
│   ├── styles/
│   │   └── globals.css           # Global styles & design tokens
│   ├── App.tsx                   # Main app component
│   └── main.tsx                  # App entry point
├── index.html
├── package.json
├── vite.config.ts
└── README.md
```

## 🎯 Key Features

### 1. Onboarding Flow
- Welcome screen with animated branding
- Work hours configuration (start/end times)
- Focus time preferences (Morning/Afternoon/Evening)
- Calendar connection setup (Google/Outlook)
- Preferences confirmation

### 2. Dashboard
- AI assistant avatar with pulsing animation
- Calendar view toggle (Day/Week/Month)
- Quick actions (Add Task, Goals, Settings)
- Calendar sync status indicator
- Integrated AI chat panel

### 3. AI Chat Interface
- Natural language task input
- Auto-parsing of task details:
  - Task title
  - Duration (e.g., "2 hours", "1h")
  - Category (work/personal/focus)
  - Deadline (e.g., "tomorrow", "next Friday")
- Task preview with confirmation

### 4. Task Management
- **Multiple Views**: List and Kanban board
- **Advanced Filtering**:
  - By category (Work/Personal/Focus)
  - By status (Scheduled/Unscheduled)
  - By time (Today/This Week/Later)
- **Statistics Dashboard**: Track progress and completion
- **AI Suggestions**: Smart recommendations for task optimization

### 5. Calendar Views
- Day view with hourly timeline
- Week view with 7-day overview
- Month view with full calendar grid
- Color-coded task categories
- Click tasks for details

## 🎨 Design System

### Colors
- **Primary**: Blue (#3B82F6) to Purple (#9333EA) gradients
- **Secondary**: Emerald (#10B981), Teal, Pink
- **Backgrounds**: Soft pastels with gradient overlays
- **Glass Effects**: Translucent panels with backdrop blur

### Typography
- Base font size: 16px
- Scale: xs, sm, base, lg, xl, 2xl, 3xl, 4xl, 6xl
- Font weights: normal (400), semibold (600), bold (700)

### Spacing
- Base unit: 0.25rem (4px)
- Scale: 1-96 units

### Custom Classes
- `.glass` - Standard glass effect
- `.glass-strong` - Enhanced glass effect
- `.soft-glow-*` - Colored shadow effects
- `.gradient-calm` - Soft multi-color gradients

## ♿ Accessibility

This application includes:
- **ARIA labels** on all interactive elements
- **Keyboard navigation** support (Tab, Enter, Escape)
- **Focus indicators** with clear visual feedback
- **Screen reader** announcements for state changes
- **Skip to content** link for navigation
- **Reduced motion** support via media queries
- **High contrast** mode support

## 🔌 API Integration

✅ **The frontend is now fully integrated with the backend!**

### Features Integrated

1. **AI Chatbot** - Chat with the AI agent for task scheduling and calendar management
2. **Google Calendar Sync** - Automatically fetch and display calendar events
3. **Real-time Updates** - Refresh calendar events with a button click
4. **Health Monitoring** - Visual indicator when backend API is offline

### Setup

1. **Configure Backend URL**:
   ```bash
   # The .env file is already created with default settings
   # Edit if your backend runs on a different port
   VITE_API_BASE_URL=http://localhost:5000
   ```

2. **Start Backend** (in another terminal):
   ```bash
   cd /Users/yashjainp44/task-ai-poc
   python app/api/app.py
   ```

3. **Start Frontend**:
   ```bash
   npm run dev
   ```

### API Endpoints Used

- `POST /chat` - AI agent conversations
- `GET /calendar/events` - Fetch Google Calendar events
- `POST /calendar/events` - Create calendar events
- `GET /health` - API health check

### Detailed Integration Guide

See [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) for comprehensive documentation on:
- Architecture overview
- Setup instructions
- Troubleshooting
- API service layer details
- Testing procedures

## 🧪 Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally

### Hot Module Replacement (HMR)

Vite provides instant HMR - changes appear immediately without full page reload.

## 📝 Next Steps

To integrate with the main application:

1. **Connect to Backend API**: Update fetch calls to point to your Flask/FastAPI backend
2. **Add Authentication**: Implement user login/session management
3. **Real Calendar Integration**: Complete Google Calendar OAuth flow
4. **State Management**: Consider adding Redux/Zustand for complex state
5. **Testing**: Add unit tests with Vitest and component tests with Testing Library

## 🐛 Known Issues

- One moderate security vulnerability in dependencies (run `npm audit fix`)
- Mock data currently used instead of real API calls

## 🔗 Related Links

- [Original Figma Design](https://www.figma.com/design/UkX6HpydvlFCQAVuExTxM5/AI-Scheduling-Assistant-UX-Flow--Copy-)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [Framer Motion Documentation](https://www.framer.com/motion/)
- [Radix UI Documentation](https://www.radix-ui.com/)

## 📄 License

This is part of the AI Scheduling Assistant project.
