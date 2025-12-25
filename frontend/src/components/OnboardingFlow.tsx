import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Sparkles, Calendar, Clock, Zap, Check, ArrowRight } from 'lucide-react';
import type { UserPreferences } from '../App';

interface OnboardingFlowProps {
  onComplete: (preferences: UserPreferences) => void;
}

export function OnboardingFlow({ onComplete }: OnboardingFlowProps) {
  const [step, setStep] = useState(0);
  const [workHoursStart, setWorkHoursStart] = useState(9);
  const [workHoursEnd, setWorkHoursEnd] = useState(17);
  const [focusTimeBlocks, setFocusTimeBlocks] = useState<string[]>(['Morning']);
  const [calendarConnected, setCalendarConnected] = useState(false);

  const handleComplete = () => {
    onComplete({
      workHoursStart,
      workHoursEnd,
      focusTimeBlocks,
      calendarConnected,
    });
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-8 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-200/30 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{ duration: 8, repeat: Infinity }}
        />
        <motion.div
          className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-200/30 rounded-full blur-3xl"
          animate={{
            scale: [1.2, 1, 1.2],
            opacity: [0.5, 0.3, 0.5],
          }}
          transition={{ duration: 8, repeat: Infinity }}
        />
      </div>

      <AnimatePresence mode="wait">
        {step === 0 && (
          <WelcomeScreen key="welcome" onNext={() => setStep(1)} />
        )}
        {step === 1 && (
          <PreferencesScreen
            key="preferences"
            workHoursStart={workHoursStart}
            workHoursEnd={workHoursEnd}
            focusTimeBlocks={focusTimeBlocks}
            calendarConnected={calendarConnected}
            onWorkHoursStartChange={setWorkHoursStart}
            onWorkHoursEndChange={setWorkHoursEnd}
            onFocusTimeBlocksChange={setFocusTimeBlocks}
            onCalendarConnectedChange={setCalendarConnected}
            onNext={() => setStep(2)}
            onBack={() => setStep(0)}
          />
        )}
        {step === 2 && (
          <CategoriesScreen key="categories" onNext={() => setStep(3)} onBack={() => setStep(1)} />
        )}
        {step === 3 && (
          <ConfirmationScreen
            key="confirmation"
            workHoursStart={workHoursStart}
            workHoursEnd={workHoursEnd}
            focusTimeBlocks={focusTimeBlocks}
            calendarConnected={calendarConnected}
            onConfirm={handleComplete}
            onBack={() => setStep(2)}
          />
        )}
      </AnimatePresence>

      {/* Progress indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex gap-2" role="progressbar" aria-valuenow={step + 1} aria-valuemin={1} aria-valuemax={4} aria-label="Onboarding progress">
        {[0, 1, 2, 3].map((i) => (
          <div
            key={i}
            className={`h-1.5 rounded-full transition-all duration-500 ${
              i === step
                ? 'w-8 bg-gradient-to-r from-blue-500 to-purple-600'
                : 'w-1.5 bg-gray-400'
            }`}
            aria-label={`Step ${i + 1} ${i === step ? 'current' : i < step ? 'completed' : 'upcoming'}`}
          />
        ))}
      </div>
    </div>
  );
}

function WelcomeScreen({ onNext }: { onNext: () => void }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="text-center max-w-2xl relative z-10"
      role="region"
      aria-label="Welcome screen"
    >
      <motion.div
        animate={{
          rotate: [0, 360],
          scale: [1, 1.1, 1],
        }}
        transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
        className="inline-block mb-8"
        aria-hidden="true"
      >
        <div className="w-32 h-32 rounded-full bg-gradient-to-br from-blue-400 via-purple-400 to-pink-400 flex items-center justify-center shadow-lg">
          <Sparkles className="w-16 h-16 text-white" aria-hidden="true" />
        </div>
      </motion.div>

      <motion.h1
        className="text-6xl mb-4 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        Welcome to Harmony
      </motion.h1>

      <motion.p
        className="text-2xl text-purple-700 mb-12"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
      >
        Plan your life with AI
      </motion.p>

      <motion.p
        className="text-gray-700 mb-12 text-lg"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
      >
        Experience intelligent scheduling that adapts to your life.
        <br />
        Let AI handle the complexity while you focus on what matters.
      </motion.p>

      <motion.button
        onClick={onNext}
        className="group relative px-12 py-4 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full overflow-hidden shadow-lg text-white hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-4 focus:ring-blue-300"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.8 }}
        whileHover={{ scale: 1.05, boxShadow: '0 8px 30px rgba(59, 130, 246, 0.4)' }}
        whileTap={{ scale: 0.95 }}
        aria-label="Get started with onboarding"
      >
        <span className="relative z-10 flex items-center gap-2 text-lg">
          Get started
          <ArrowRight className="w-5 h-5" aria-hidden="true" />
        </span>
      </motion.button>
    </motion.div>
  );
}

function PreferencesScreen({
  workHoursStart,
  workHoursEnd,
  focusTimeBlocks,
  calendarConnected,
  onWorkHoursStartChange,
  onWorkHoursEndChange,
  onFocusTimeBlocksChange,
  onCalendarConnectedChange,
  onNext,
  onBack,
}: {
  workHoursStart: number;
  workHoursEnd: number;
  focusTimeBlocks: string[];
  calendarConnected: boolean;
  onWorkHoursStartChange: (value: number) => void;
  onWorkHoursEndChange: (value: number) => void;
  onFocusTimeBlocksChange: (value: string[]) => void;
  onCalendarConnectedChange: (value: boolean) => void;
  onNext: () => void;
  onBack: () => void;
}) {
  const focusOptions = ['Morning', 'Afternoon', 'Evening'];

  const toggleFocusBlock = (block: string) => {
    if (focusTimeBlocks.includes(block)) {
      onFocusTimeBlocksChange(focusTimeBlocks.filter(b => b !== block));
    } else {
      onFocusTimeBlocksChange([...focusTimeBlocks, block]);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="max-w-2xl w-full relative z-10"
      role="region"
      aria-label="Preferences setup"
    >
      <div className="glass-strong rounded-3xl p-12 shadow-xl">
        <div className="flex items-center gap-4 mb-8">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-400 to-purple-400 flex items-center justify-center shadow-md" aria-hidden="true">
            <Calendar className="w-8 h-8 text-white" />
          </div>
          <div>
            <h2 className="text-3xl text-gray-900">Set your preferences</h2>
            <p className="text-gray-600">Help AI understand your schedule</p>
          </div>
        </div>

        {/* Work Hours */}
        <fieldset className="mb-8">
          <legend className="block text-blue-700 mb-4 flex items-center gap-2 font-semibold">
            <Clock className="w-5 h-5" aria-hidden="true" />
            Work hours
          </legend>
          <div className="flex items-center gap-6">
            <div className="flex-1">
              <div className="bg-white/80 rounded-xl p-4 shadow-sm border border-blue-100">
                <label htmlFor="work-hours-start" className="text-sm text-gray-600 mb-2 block">
                  Start
                </label>
                <input
                  id="work-hours-start"
                  type="range"
                  min="0"
                  max="23"
                  value={workHoursStart}
                  onChange={(e) => onWorkHoursStartChange(Number(e.target.value))}
                  className="w-full accent-blue-600"
                  aria-label={`Work hours start time: ${workHoursStart}:00`}
                  aria-valuemin={0}
                  aria-valuemax={23}
                  aria-valuenow={workHoursStart}
                />
                <div className="text-2xl text-gray-900 mt-2" aria-live="polite">
                  {workHoursStart.toString().padStart(2, '0')}:00
                </div>
              </div>
            </div>
            <div className="text-gray-500" aria-hidden="true">to</div>
            <div className="flex-1">
              <div className="bg-white/80 rounded-xl p-4 shadow-sm border border-purple-100">
                <label htmlFor="work-hours-end" className="text-sm text-gray-600 mb-2 block">
                  End
                </label>
                <input
                  id="work-hours-end"
                  type="range"
                  min="0"
                  max="23"
                  value={workHoursEnd}
                  onChange={(e) => onWorkHoursEndChange(Number(e.target.value))}
                  className="w-full accent-purple-600"
                  aria-label={`Work hours end time: ${workHoursEnd}:00`}
                  aria-valuemin={0}
                  aria-valuemax={23}
                  aria-valuenow={workHoursEnd}
                />
                <div className="text-2xl text-gray-900 mt-2" aria-live="polite">
                  {workHoursEnd.toString().padStart(2, '0')}:00
                </div>
              </div>
            </div>
          </div>
        </fieldset>

        {/* Focus Time Blocks */}
        <fieldset className="mb-8">
          <legend className="block text-purple-700 mb-4 flex items-center gap-2 font-semibold">
            <Zap className="w-5 h-5" aria-hidden="true" />
            Preferred Focus Time
          </legend>
          <div className="flex gap-3" role="group" aria-label="Focus time preferences">
            {focusOptions.map((option) => (
              <button
                key={option}
                onClick={() => toggleFocusBlock(option)}
                className={`flex-1 py-4 rounded-xl transition-all duration-300 focus:outline-none focus:ring-4 focus:ring-purple-300 ${
                  focusTimeBlocks.includes(option)
                    ? 'bg-gradient-to-r from-purple-500 to-pink-500 shadow-md text-white'
                    : 'bg-white/80 border-2 border-gray-300 text-gray-700 hover:border-purple-400'
                }`}
                aria-pressed={focusTimeBlocks.includes(option)}
                aria-label={`${option} focus time ${focusTimeBlocks.includes(option) ? 'selected' : 'not selected'}`}
              >
                <div className="flex items-center justify-center gap-2">
                  {focusTimeBlocks.includes(option) && <Check className="w-5 h-5" aria-hidden="true" />}
                  <span>{option}</span>
                </div>
              </button>
            ))}
          </div>
        </fieldset>

        {/* Calendar Connection */}
        <fieldset className="mb-8">
          <legend className="block text-emerald-700 mb-4 font-semibold">Connect calendar</legend>
          <div className="flex gap-3" role="group" aria-label="Calendar connection options">
            <button
              onClick={() => onCalendarConnectedChange(!calendarConnected)}
              className={`flex-1 py-4 px-6 rounded-xl transition-all duration-300 focus:outline-none focus:ring-4 focus:ring-emerald-300 ${
                calendarConnected
                  ? 'bg-gradient-to-r from-emerald-500 to-teal-500 shadow-md text-white'
                  : 'bg-white/80 border-2 border-gray-300 text-gray-700 hover:border-emerald-400'
              }`}
              aria-pressed={calendarConnected}
              aria-label={`Google Calendar ${calendarConnected ? 'connected' : 'not connected'}`}
            >
              <div className="flex items-center justify-center gap-2">
                {calendarConnected && <Check className="w-5 h-5" aria-hidden="true" />}
                <span>Google Calendar</span>
              </div>
            </button>
            <button 
              className="flex-1 py-4 px-6 rounded-xl bg-white/80 border-2 border-gray-300 text-gray-700 hover:border-blue-400 transition-all focus:outline-none focus:ring-4 focus:ring-blue-300"
              aria-label="Connect Outlook calendar"
            >
              <span>Outlook</span>
            </button>
          </div>
        </fieldset>

        {/* Navigation */}
        <nav className="flex gap-4" aria-label="Onboarding navigation">
          <button
            onClick={onBack}
            className="px-8 py-3 rounded-xl bg-white border-2 border-gray-400 text-gray-800 hover:border-gray-500 hover:bg-gray-50 transition-all focus:outline-none focus:ring-4 focus:ring-gray-300"
            aria-label="Go back to previous step"
          >
            Back
          </button>
          <button
            onClick={onNext}
            className="flex-1 px-8 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-md hover:from-blue-700 hover:to-purple-700 hover:shadow-lg hover:scale-105 transition-all focus:outline-none focus:ring-4 focus:ring-blue-300"
            aria-label="Continue to next step"
          >
            Continue
          </button>
        </nav>
      </div>
    </motion.div>
  );
}

function CategoriesScreen({ onNext, onBack }: { onNext: () => void; onBack: () => void }) {
  const categories = [
    {
      name: 'Work',
      color: 'blue',
      gradient: 'from-blue-400 to-blue-500',
      icon: '💼',
      description: 'Professional tasks, meetings, and projects',
      shadow: 'soft-glow-blue',
    },
    {
      name: 'Personal',
      color: 'purple',
      gradient: 'from-purple-400 to-pink-500',
      icon: '✨',
      description: 'Personal errands, hobbies, and self-care',
      shadow: 'soft-glow-purple',
    },
    {
      name: 'Focus Time',
      color: 'green',
      gradient: 'from-emerald-400 to-teal-500',
      icon: '🎯',
      description: 'Deep work sessions for maximum productivity',
      shadow: 'soft-glow-green',
    },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="max-w-4xl w-full relative z-10"
      role="region"
      aria-label="Task categories introduction"
    >
      <div className="text-center mb-12">
        <h2 className="text-4xl text-gray-900 mb-3">Task categories</h2>
        <p className="text-gray-700">AI will organize your tasks into these categories</p>
      </div>

      <div className="grid grid-cols-3 gap-6 mb-12" role="list" aria-label="Available task categories">
        {categories.map((category, index) => (
          <motion.div
            key={category.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`glass-strong rounded-2xl p-8 border-2 border-${category.color}-300 ${category.shadow} hover:scale-105 transition-all cursor-pointer focus:outline-none focus:ring-4 focus:ring-${category.color}-300`}
            role="listitem"
            tabIndex={0}
            aria-label={`${category.name} category: ${category.description}`}
          >
            <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${category.gradient} flex items-center justify-center mb-4 text-3xl shadow-md`} aria-hidden="true">
              {category.icon}
            </div>
            <h3 className="text-2xl text-gray-900 mb-2">{category.name}</h3>
            <div className={`w-12 h-1 rounded-full bg-gradient-to-r ${category.gradient} mb-4`} aria-hidden="true" />
            <p className="text-gray-600 text-sm">{category.description}</p>
          </motion.div>
        ))}
      </div>

      {/* Navigation */}
      <nav className="flex gap-4 justify-center" aria-label="Onboarding navigation">
        <button
          onClick={onBack}
          className="px-8 py-3 rounded-xl bg-white border-2 border-gray-400 text-gray-800 hover:border-gray-500 hover:bg-gray-50 transition-all focus:outline-none focus:ring-4 focus:ring-gray-300"
          aria-label="Go back to previous step"
        >
          Back
        </button>
        <button
          onClick={onNext}
          className="px-12 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-md hover:from-blue-700 hover:to-purple-700 hover:shadow-lg hover:scale-105 transition-all focus:outline-none focus:ring-4 focus:ring-blue-300"
          aria-label="Continue to next step"
        >
          Continue
        </button>
      </nav>
    </motion.div>
  );
}

function ConfirmationScreen({
  workHoursStart,
  workHoursEnd,
  focusTimeBlocks,
  calendarConnected,
  onConfirm,
  onBack,
}: {
  workHoursStart: number;
  workHoursEnd: number;
  focusTimeBlocks: string[];
  calendarConnected: boolean;
  onConfirm: () => void;
  onBack: () => void;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="max-w-2xl w-full relative z-10"
      role="region"
      aria-label="Setup confirmation"
    >
      <div className="glass-strong rounded-3xl p-12 shadow-xl">
        <div className="text-center mb-8">
          <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-400 to-purple-400 flex items-center justify-center mx-auto mb-4 shadow-lg" aria-hidden="true">
            <Check className="w-10 h-10 text-white" />
          </div>
          <h2 className="text-3xl text-gray-900 mb-2">You're all set!</h2>
          <p className="text-gray-600">Review your preferences below</p>
        </div>

        <div className="space-y-4 mb-8" role="list" aria-label="Your preferences summary">
          <div className="bg-white/80 rounded-xl p-6 shadow-sm border border-blue-200" role="listitem">
            <div className="flex items-center gap-3 mb-2">
              <Clock className="w-5 h-5 text-blue-600" aria-hidden="true" />
              <span className="text-sm text-gray-700 font-semibold">Work hours</span>
            </div>
            <div className="text-xl text-gray-900">
              {workHoursStart.toString().padStart(2, '0')}:00 - {workHoursEnd.toString().padStart(2, '0')}:00
            </div>
          </div>

          <div className="bg-white/80 rounded-xl p-6 shadow-sm border border-purple-200" role="listitem">
            <div className="flex items-center gap-3 mb-2">
              <Zap className="w-5 h-5 text-purple-600" aria-hidden="true" />
              <span className="text-sm text-gray-700 font-semibold">Focus Time Blocks</span>
            </div>
            <div className="flex gap-2">
              {focusTimeBlocks.map((block) => (
                <span
                  key={block}
                  className="px-3 py-1 rounded-full bg-gradient-to-r from-purple-400 to-pink-400 text-sm text-white shadow-sm"
                >
                  {block}
                </span>
              ))}
            </div>
          </div>

          <div className="bg-white/80 rounded-xl p-6 shadow-sm border border-emerald-200" role="listitem">
            <div className="flex items-center gap-3 mb-2">
              <Calendar className="w-5 h-5 text-emerald-600" aria-hidden="true" />
              <span className="text-sm text-gray-700 font-semibold">Calendar Connection</span>
            </div>
            <div className="text-xl text-gray-900">
              {calendarConnected ? 'Google Calendar Connected' : 'Not Connected'}
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex gap-4" aria-label="Final navigation">
          <button
            onClick={onBack}
            className="px-8 py-3 rounded-xl bg-white border-2 border-gray-400 text-gray-800 hover:border-gray-500 hover:bg-gray-50 transition-all focus:outline-none focus:ring-4 focus:ring-gray-300"
            aria-label="Go back to previous step"
          >
            Back
          </button>
          <button
            onClick={onConfirm}
            className="flex-1 px-8 py-4 rounded-xl bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 text-white shadow-lg hover:from-blue-700 hover:via-purple-700 hover:to-pink-700 hover:shadow-xl hover:scale-105 transition-all text-lg flex items-center justify-center gap-2 focus:outline-none focus:ring-4 focus:ring-blue-300"
            aria-label="Generate your schedule and complete onboarding"
          >
            <Sparkles className="w-5 h-5" aria-hidden="true" />
            Generate my schedule
          </button>
        </nav>
      </div>
    </motion.div>
  );
}