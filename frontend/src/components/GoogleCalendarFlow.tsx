import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Calendar, Check, Shield, RefreshCw, AlertCircle, Settings, X, ChevronRight, Lock, Zap, Clock, Globe } from 'lucide-react';

type FlowStep = 'intro' | 'permissions' | 'oauth' | 'success' | 'syncing' | 'conflict-intro' | 'complete';

interface GoogleCalendarFlowProps {
  onComplete: () => void;
  onCancel: () => void;
}

export function GoogleCalendarFlow({ onComplete, onCancel }: GoogleCalendarFlowProps) {
  const [currentStep, setCurrentStep] = useState<FlowStep>('intro');
  const [syncProgress, setSyncProgress] = useState(0);

  // Simulate sync progress
  React.useEffect(() => {
    if (currentStep === 'syncing') {
      const interval = setInterval(() => {
        setSyncProgress((prev) => {
          if (prev >= 100) {
            clearInterval(interval);
            setTimeout(() => setCurrentStep('conflict-intro'), 500);
            return 100;
          }
          return prev + 10;
        });
      }, 300);
      return () => clearInterval(interval);
    }
  }, [currentStep]);

  const handleConnect = () => {
    setCurrentStep('permissions');
  };

  const handleContinueToGoogle = () => {
    setCurrentStep('oauth');
  };

  const handleOAuthSuccess = () => {
    setCurrentStep('success');
  };

  const handleStartSync = () => {
    setCurrentStep('syncing');
    setSyncProgress(0);
  };

  const handleConflictIntroComplete = () => {
    setCurrentStep('complete');
    setTimeout(onComplete, 500);
  };

  return (
    <div className="fixed inset-0 bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 z-50 flex items-center justify-center p-8">
      <AnimatePresence mode="wait">
        {currentStep === 'intro' && (
          <IntroScreen key="intro" onConnect={handleConnect} onCancel={onCancel} />
        )}
        {currentStep === 'permissions' && (
          <PermissionsScreen key="permissions" onContinue={handleContinueToGoogle} onBack={() => setCurrentStep('intro')} />
        )}
        {currentStep === 'oauth' && (
          <OAuthScreen key="oauth" onSuccess={handleOAuthSuccess} onCancel={onCancel} />
        )}
        {currentStep === 'success' && (
          <SuccessScreen key="success" onContinue={handleStartSync} />
        )}
        {currentStep === 'syncing' && (
          <SyncingScreen key="syncing" progress={syncProgress} />
        )}
        {currentStep === 'conflict-intro' && (
          <ConflictIntroScreen key="conflict-intro" onContinue={handleConflictIntroComplete} />
        )}
      </AnimatePresence>
    </div>
  );
}

function IntroScreen({ onConnect, onCancel }: { onConnect: () => void; onCancel: () => void }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="max-w-2xl w-full"
      role="dialog"
      aria-labelledby="connect-calendar-title"
      aria-modal="true"
    >
      <div className="glass-strong rounded-3xl p-12 shadow-xl border-2 border-blue-300 relative overflow-hidden">
        {/* Background decoration */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-blue-200/30 rounded-full blur-3xl pointer-events-none" aria-hidden="true" />
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-purple-200/30 rounded-full blur-3xl pointer-events-none" aria-hidden="true" />

        <div className="relative z-10 text-center">
          {/* Google Calendar Icon */}
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
            className="inline-flex items-center justify-center mb-8"
          >
            <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center shadow-lg" aria-hidden="true">
              <Calendar className="w-12 h-12 text-white" />
            </div>
          </motion.div>

          <motion.h2
            id="connect-calendar-title"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="text-3xl text-gray-900 mb-4"
          >
            Sync your calendar with AI intelligence
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="text-gray-600 mb-8 text-lg max-w-lg mx-auto"
          >
            Connect your Google Calendar to enable smart scheduling, conflict detection, and automatic rescheduling.
          </motion.p>

          {/* Benefits */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="grid grid-cols-2 gap-4 mb-8"
          >
            {[
              { icon: RefreshCw, text: 'Auto-sync events' },
              { icon: Zap, text: 'Smart conflict detection' },
              { icon: Clock, text: 'Automatic rescheduling' },
              { icon: Globe, text: 'Cross-device sync' },
            ].map((benefit, index) => (
              <div
                key={index}
                className="bg-white/80 rounded-xl p-4 border border-blue-200 shadow-sm"
              >
                <benefit.icon className="w-5 h-5 text-blue-600 mx-auto mb-2" aria-hidden="true" />
                <p className="text-sm text-gray-700">{benefit.text}</p>
              </div>
            ))}
          </motion.div>

          {/* Actions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="flex gap-4"
          >
            <button
              onClick={onCancel}
              className="flex-1 px-6 py-3 rounded-xl bg-white border-2 border-gray-400 text-gray-800 hover:border-gray-500 hover:bg-gray-50 transition-all focus:outline-none focus:ring-4 focus:ring-gray-300"
              aria-label="Cancel calendar connection"
            >
              Maybe later
            </button>
            <button
              onClick={onConnect}
              className="flex-1 px-6 py-4 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg hover:from-blue-700 hover:to-purple-700 hover:shadow-xl hover:scale-105 transition-all flex items-center justify-center gap-2 focus:outline-none focus:ring-4 focus:ring-blue-300"
              aria-label="Connect Google Calendar"
            >
              <Calendar className="w-5 h-5" aria-hidden="true" />
              Connect Google Calendar
            </button>
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
}

function PermissionsScreen({ onContinue, onBack }: { onContinue: () => void; onBack: () => void }) {
  const permissions = [
    {
      icon: Calendar,
      title: 'View your calendar events',
      description: 'Read your existing events to prevent scheduling conflicts',
      color: 'blue',
    },
    {
      icon: RefreshCw,
      title: 'Add and update events',
      description: 'Create new events and modify AI-scheduled tasks',
      color: 'purple',
    },
    {
      icon: Zap,
      title: 'Automatically reschedule tasks',
      description: 'Move tasks when conflicts occur based on your preferences',
      color: 'emerald',
    },
    {
      icon: Globe,
      title: 'Sync your tasks across devices',
      description: 'Keep your schedule updated on all your devices',
      color: 'pink',
    },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="max-w-3xl w-full"
      role="dialog"
      aria-labelledby="permissions-title"
      aria-modal="true"
    >
      <div className="glass-strong rounded-3xl p-8 shadow-xl border-2 border-purple-300">
        <div className="flex items-start justify-between mb-8">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center shadow-md" aria-hidden="true">
              <Shield className="w-7 h-7 text-white" />
            </div>
            <div>
              <h2 id="permissions-title" className="text-2xl text-gray-900">Permissions required</h2>
              <p className="text-sm text-gray-600">Review what this app will access</p>
            </div>
          </div>
        </div>

        <div className="space-y-3 mb-8" role="list" aria-label="Required permissions">
          {permissions.map((permission, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white/80 rounded-xl p-5 border-2 border-gray-200 hover:border-gray-300 transition-all shadow-sm"
              role="listitem"
            >
              <div className="flex items-start gap-4">
                <div className={`w-10 h-10 rounded-lg bg-gradient-to-br from-${permission.color}-400 to-${permission.color}-500 flex items-center justify-center shrink-0 shadow-sm`} aria-hidden="true">
                  <permission.icon className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="text-gray-900 font-semibold">{permission.title}</h3>
                    <Check className="w-5 h-5 text-emerald-600" aria-label="Required" />
                  </div>
                  <p className="text-sm text-gray-600">{permission.description}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Security Notice */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-blue-50 rounded-xl p-4 border-2 border-blue-300 mb-8"
        >
          <div className="flex items-start gap-3">
            <Lock className="w-5 h-5 text-blue-700 shrink-0 mt-0.5" aria-hidden="true" />
            <div>
              <h4 className="text-sm font-semibold text-blue-900 mb-1">Your data is secure</h4>
              <p className="text-sm text-blue-800">
                Your calendar data is encrypted and never shared with third parties. You can revoke access anytime from settings.
              </p>
            </div>
          </div>
        </motion.div>

        {/* Actions */}
        <div className="flex gap-4">
          <button
            onClick={onBack}
            className="px-6 py-3 rounded-xl bg-white border-2 border-gray-400 text-gray-800 hover:border-gray-500 hover:bg-gray-50 transition-all focus:outline-none focus:ring-4 focus:ring-gray-300"
            aria-label="Go back"
          >
            Back
          </button>
          <button
            onClick={onContinue}
            className="flex-1 px-6 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-md hover:from-blue-700 hover:to-purple-700 hover:shadow-lg hover:scale-105 transition-all flex items-center justify-center gap-2 focus:outline-none focus:ring-4 focus:ring-blue-300"
          >
            Continue to Google
            <ChevronRight className="w-5 h-5" aria-hidden="true" />
          </button>
        </div>
      </div>
    </motion.div>
  );
}

function OAuthScreen({ onSuccess, onCancel }: { onSuccess: () => void; onCancel: () => void }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="max-w-lg w-full"
      role="dialog"
      aria-labelledby="oauth-title"
      aria-modal="true"
    >
      <div className="glass-strong rounded-3xl p-8 shadow-xl border-2 border-gray-200">
        {/* Mock Google OAuth */}
        <div className="text-center mb-6">
          <div className="w-12 h-12 bg-white rounded-full mx-auto mb-4 flex items-center justify-center shadow-md">
            <span className="text-2xl" role="img" aria-label="Google">G</span>
          </div>
          <h2 id="oauth-title" className="text-xl text-gray-900 mb-2">Sign in with Google</h2>
          <p className="text-sm text-gray-600">to continue to Harmony AI Scheduler</p>
        </div>

        {/* Mock Account Selection */}
        <div className="space-y-3 mb-6">
          <button
            onClick={onSuccess}
            className="w-full bg-white rounded-xl p-4 border-2 border-gray-300 hover:border-blue-400 hover:bg-blue-50 transition-all flex items-center gap-3 focus:outline-none focus:ring-4 focus:ring-blue-300"
            aria-label="Select Google account yashjaincp@gmail.com"
          >
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-purple-400 flex items-center justify-center text-white font-semibold" aria-hidden="true">
              Y
            </div>
            <div className="text-left">
              <div className="text-gray-900 font-semibold">Yash Jain</div>
              <div className="text-sm text-gray-600">yashjaincp@gmail.com</div>
            </div>
          </button>

          <button className="w-full bg-white rounded-xl p-4 border-2 border-gray-300 hover:border-gray-400 transition-all text-gray-700 focus:outline-none focus:ring-4 focus:ring-gray-300">
            Use another account
          </button>
        </div>

        {/* Consent Text */}
        <div className="bg-gray-50 rounded-xl p-4 mb-6 border border-gray-200">
          <p className="text-xs text-gray-600 leading-relaxed">
            By continuing, Google will share your name, email address, and profile picture with Harmony. 
            This app will have access to view and manage your Google Calendar events.
          </p>
        </div>

        <button
          onClick={onCancel}
          className="w-full px-4 py-2 rounded-xl bg-white border-2 border-gray-400 text-gray-800 hover:border-gray-500 hover:bg-gray-50 transition-all focus:outline-none focus:ring-4 focus:ring-gray-300"
        >
          Cancel
        </button>
      </div>
    </motion.div>
  );
}

function SuccessScreen({ onContinue }: { onContinue: () => void }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="max-w-xl w-full text-center"
      role="dialog"
      aria-labelledby="success-title"
      aria-modal="true"
    >
      <div className="glass-strong rounded-3xl p-12 shadow-xl border-2 border-emerald-300 relative overflow-hidden">
        {/* Background decoration */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-200/30 rounded-full blur-3xl pointer-events-none" aria-hidden="true" />

        <div className="relative z-10">
          {/* Success Animation */}
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 200, delay: 0.2 }}
            className="inline-block mb-6"
          >
            <div className="w-24 h-24 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center shadow-lg" aria-hidden="true">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.4, type: 'spring', stiffness: 300 }}
              >
                <Check className="w-12 h-12 text-white" />
              </motion.div>
            </div>
          </motion.div>

          <motion.h2
            id="success-title"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="text-3xl text-gray-900 mb-3"
          >
            Your calendar is now connected!
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="text-gray-600 mb-8 text-lg"
          >
            I'll sync your events and start optimizing your schedule.
          </motion.p>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.7 }}
            className="text-sm text-gray-500 mb-8"
          >
            <Lock className="w-4 h-4 inline mr-2" aria-hidden="true" />
            Your data is encrypted and never shared
          </motion.div>

          <motion.button
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
            onClick={onContinue}
            className="px-8 py-4 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-lg hover:from-emerald-700 hover:to-teal-700 hover:shadow-xl hover:scale-105 transition-all focus:outline-none focus:ring-4 focus:ring-emerald-300"
          >
            Proceed to my schedule
          </motion.button>
        </div>
      </div>
    </motion.div>
  );
}

function SyncingScreen({ progress }: { progress: number }) {
  const steps = [
    'Scanning your existing events',
    'Importing meetings',
    'Mapping time blocks',
    'Preparing your optimized schedule',
  ];

  const currentStepIndex = Math.floor((progress / 100) * steps.length);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="max-w-xl w-full text-center"
      role="status"
      aria-live="polite"
      aria-label={`Syncing calendar: ${progress}% complete`}
    >
      <div className="glass-strong rounded-3xl p-12 shadow-xl border-2 border-blue-300">
        {/* Animated Sync Icon */}
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
          className="inline-block mb-6"
        >
          <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-400 to-purple-400 flex items-center justify-center shadow-lg" aria-hidden="true">
            <RefreshCw className="w-10 h-10 text-white" />
          </div>
        </motion.div>

        <h2 className="text-2xl text-gray-900 mb-2">Syncing your calendar</h2>
        <p className="text-gray-600 mb-8">This will only take a moment...</p>

        {/* Progress Ring */}
        <div className="relative w-32 h-32 mx-auto mb-8">
          <svg className="w-32 h-32 transform -rotate-90">
            <circle
              cx="64"
              cy="64"
              r="56"
              stroke="currentColor"
              strokeWidth="8"
              fill="none"
              className="text-gray-200"
            />
            <motion.circle
              cx="64"
              cy="64"
              r="56"
              stroke="currentColor"
              strokeWidth="8"
              fill="none"
              strokeLinecap="round"
              className="text-blue-600"
              initial={{ strokeDasharray: '0 352' }}
              animate={{ strokeDasharray: `${(progress / 100) * 352} 352` }}
              transition={{ duration: 0.3 }}
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-2xl font-bold text-gray-900">{progress}%</span>
          </div>
        </div>

        {/* Status Steps */}
        <div className="space-y-2">
          {steps.map((step, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: index <= currentStepIndex ? 1 : 0.3, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-center gap-3 justify-center"
            >
              {index < currentStepIndex ? (
                <Check className="w-5 h-5 text-emerald-600" aria-hidden="true" />
              ) : index === currentStepIndex ? (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                >
                  <RefreshCw className="w-5 h-5 text-blue-600" aria-hidden="true" />
                </motion.div>
              ) : (
                <div className="w-5 h-5 rounded-full border-2 border-gray-300" aria-hidden="true" />
              )}
              <span className={`text-sm ${index <= currentStepIndex ? 'text-gray-900' : 'text-gray-400'}`}>
                {step}
              </span>
            </motion.div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}

function ConflictIntroScreen({ onContinue }: { onContinue: () => void }) {
  const features = [
    {
      icon: AlertCircle,
      title: 'Overlapping events',
      description: 'I detect when tasks conflict with existing events',
      color: 'orange',
    },
    {
      icon: Zap,
      title: 'Smart task shifting',
      description: 'I suggest the best time to move conflicting tasks',
      color: 'purple',
    },
    {
      icon: Calendar,
      title: 'Daily vs weekly rescheduling',
      description: 'Choose how aggressively I optimize your schedule',
      color: 'blue',
    },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="max-w-3xl w-full"
      role="dialog"
      aria-labelledby="conflict-intro-title"
      aria-modal="true"
    >
      <div className="glass-strong rounded-3xl p-8 shadow-xl border-2 border-purple-300">
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center mx-auto mb-4 shadow-md" aria-hidden="true">
            <Zap className="w-8 h-8 text-white" />
          </div>
          <h2 id="conflict-intro-title" className="text-2xl text-gray-900 mb-2">
            How I handle conflicts
          </h2>
          <p className="text-gray-600">
            When a conflict occurs, I'll suggest the best way to reorganize your time
          </p>
        </div>

        <div className="grid gap-4 mb-8">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white/80 rounded-xl p-6 border-2 border-gray-200 shadow-sm"
            >
              <div className="flex items-start gap-4">
                <div className={`w-12 h-12 rounded-lg bg-gradient-to-br from-${feature.color}-400 to-${feature.color}-500 flex items-center justify-center shrink-0 shadow-sm`} aria-hidden="true">
                  <feature.icon className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-gray-900 font-semibold mb-1">{feature.title}</h3>
                  <p className="text-sm text-gray-600">{feature.description}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        <motion.button
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          onClick={onContinue}
          className="w-full px-6 py-4 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg hover:from-purple-700 hover:to-pink-700 hover:shadow-xl hover:scale-105 transition-all focus:outline-none focus:ring-4 focus:ring-purple-300"
        >
          Got it
        </motion.button>
      </div>
    </motion.div>
  );
}
