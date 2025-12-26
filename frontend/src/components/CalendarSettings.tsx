import React, { useState } from 'react';
import { motion } from 'motion/react';
import { Calendar, Shield, RefreshCw, Settings as SettingsIcon, LogOut, Check, X, AlertTriangle } from 'lucide-react';

interface CalendarSettingsProps {
  isConnected: boolean;
  userEmail?: string;
  onDisconnect: () => void;
  onClose: () => void;
}

export function CalendarSettings({ isConnected, userEmail = 'yashjaincp@gmail.com', onDisconnect, onClose }: CalendarSettingsProps) {
  const [syncDirection, setSyncDirection] = useState<'two-way' | 'read-only'>('two-way');
  const [writeEvents, setWriteEvents] = useState(true);
  const [modifyEvents, setModifyEvents] = useState(true);
  const [deleteEvents, setDeleteEvents] = useState(false);
  const [showDisconnectConfirm, setShowDisconnectConfirm] = useState(false);

  const handleDisconnect = () => {
    onDisconnect();
    setShowDisconnectConfirm(false);
    onClose();
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-8"
      onClick={onClose}
      role="dialog"
      aria-labelledby="calendar-settings-title"
      aria-modal="true"
    >
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        onClick={(e) => e.stopPropagation()}
        className="glass-strong rounded-3xl p-8 max-w-2xl w-full border-2 border-blue-300 shadow-xl relative overflow-hidden"
      >
        {/* Background decoration */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-blue-200/30 rounded-full blur-3xl pointer-events-none" aria-hidden="true" />

        <div className="relative z-10">
          {/* Header */}
          <div className="flex items-start justify-between mb-8">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-blue-400 to-purple-400 flex items-center justify-center shadow-md" aria-hidden="true">
                <SettingsIcon className="w-7 h-7 text-white" />
              </div>
              <div>
                <h2 id="calendar-settings-title" className="text-2xl text-gray-900">Calendar sync settings</h2>
                <p className="text-sm text-gray-600">Manage your Google Calendar connection</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-lg bg-white/80 border border-gray-300 hover:border-gray-400 transition-all focus:outline-none focus:ring-4 focus:ring-blue-300"
              aria-label="Close settings"
            >
              <X className="w-5 h-5 text-gray-700" />
            </button>
          </div>

          {/* Connected Account */}
          <section className="mb-8" aria-labelledby="connected-account-heading">
            <h3 id="connected-account-heading" className="text-sm text-gray-700 mb-3 font-semibold flex items-center gap-2">
              <Calendar className="w-4 h-4" aria-hidden="true" />
              Connected account
            </h3>
            <div className="bg-white/80 rounded-xl p-5 border-2 border-emerald-300 shadow-sm">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-purple-400 flex items-center justify-center text-white font-semibold" aria-hidden="true">
                    {userEmail.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <div className="text-gray-900 font-semibold">{userEmail}</div>
                    <div className="text-sm text-emerald-700 flex items-center gap-1">
                      <Check className="w-4 h-4" aria-hidden="true" />
                      Connected
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => setShowDisconnectConfirm(true)}
                  className="px-4 py-2 rounded-lg bg-white border-2 border-red-400 text-red-700 hover:bg-red-50 transition-all flex items-center gap-2 focus:outline-none focus:ring-4 focus:ring-red-300"
                  aria-label="Disconnect Google Calendar"
                >
                  <LogOut className="w-4 h-4" aria-hidden="true" />
                  Disconnect
                </button>
              </div>
            </div>
          </section>

          {/* Sync Direction */}
          <section className="mb-8" aria-labelledby="sync-direction-heading">
            <h3 id="sync-direction-heading" className="text-sm text-gray-700 mb-3 font-semibold flex items-center gap-2">
              <RefreshCw className="w-4 h-4" aria-hidden="true" />
              Sync direction
            </h3>
            <div className="space-y-3" role="radiogroup" aria-labelledby="sync-direction-heading">
              <button
                onClick={() => setSyncDirection('two-way')}
                className={`w-full bg-white/80 rounded-xl p-4 border-2 transition-all text-left focus:outline-none focus:ring-4 focus:ring-blue-300 ${
                  syncDirection === 'two-way'
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
                role="radio"
                aria-checked={syncDirection === 'two-way'}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="text-gray-900 font-semibold mb-1">Two-way sync (recommended)</div>
                    <div className="text-sm text-gray-600">
                      Changes in either Google Calendar or this app will sync both ways
                    </div>
                  </div>
                  {syncDirection === 'two-way' && (
                    <Check className="w-5 h-5 text-blue-600 shrink-0" aria-hidden="true" />
                  )}
                </div>
              </button>

              <button
                onClick={() => setSyncDirection('read-only')}
                className={`w-full bg-white/80 rounded-xl p-4 border-2 transition-all text-left focus:outline-none focus:ring-4 focus:ring-blue-300 ${
                  syncDirection === 'read-only'
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
                role="radio"
                aria-checked={syncDirection === 'read-only'}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="text-gray-900 font-semibold mb-1">Read-only</div>
                    <div className="text-sm text-gray-600">
                      Only import events from Google Calendar, don't write back
                    </div>
                  </div>
                  {syncDirection === 'read-only' && (
                    <Check className="w-5 h-5 text-blue-600 shrink-0" aria-hidden="true" />
                  )}
                </div>
              </button>
            </div>
          </section>

          {/* Permissions Toggle Panel */}
          <section className="mb-8" aria-labelledby="permissions-heading">
            <h3 id="permissions-heading" className="text-sm text-gray-700 mb-3 font-semibold flex items-center gap-2">
              <Shield className="w-4 h-4" aria-hidden="true" />
              Permissions
            </h3>
            <div className="bg-white/80 rounded-xl p-5 border-2 border-gray-200 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-gray-900 font-semibold">Write new events</div>
                  <div className="text-sm text-gray-600">Allow app to create new calendar events</div>
                </div>
                <button
                  onClick={() => setWriteEvents(!writeEvents)}
                  className={`relative w-14 h-7 rounded-full transition-colors focus:outline-none focus:ring-4 focus:ring-blue-300 ${
                    writeEvents ? 'bg-blue-600' : 'bg-gray-300'
                  }`}
                  role="switch"
                  aria-checked={writeEvents}
                  aria-label="Toggle write new events permission"
                >
                  <motion.div
                    className="absolute top-0.5 left-0.5 w-6 h-6 bg-white rounded-full shadow-md"
                    animate={{ x: writeEvents ? 28 : 0 }}
                    transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                  />
                </button>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <div className="text-gray-900 font-semibold">Modify existing events</div>
                  <div className="text-sm text-gray-600">Allow app to update calendar events</div>
                </div>
                <button
                  onClick={() => setModifyEvents(!modifyEvents)}
                  className={`relative w-14 h-7 rounded-full transition-colors focus:outline-none focus:ring-4 focus:ring-blue-300 ${
                    modifyEvents ? 'bg-blue-600' : 'bg-gray-300'
                  }`}
                  role="switch"
                  aria-checked={modifyEvents}
                  aria-label="Toggle modify existing events permission"
                >
                  <motion.div
                    className="absolute top-0.5 left-0.5 w-6 h-6 bg-white rounded-full shadow-md"
                    animate={{ x: modifyEvents ? 28 : 0 }}
                    transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                  />
                </button>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <div className="text-gray-900 font-semibold">Delete or move tasks</div>
                  <div className="text-sm text-gray-600">Allow app to delete calendar events</div>
                </div>
                <button
                  onClick={() => setDeleteEvents(!deleteEvents)}
                  className={`relative w-14 h-7 rounded-full transition-colors focus:outline-none focus:ring-4 focus:ring-blue-300 ${
                    deleteEvents ? 'bg-blue-600' : 'bg-gray-300'
                  }`}
                  role="switch"
                  aria-checked={deleteEvents}
                  aria-label="Toggle delete or move tasks permission"
                >
                  <motion.div
                    className="absolute top-0.5 left-0.5 w-6 h-6 bg-white rounded-full shadow-md"
                    animate={{ x: deleteEvents ? 28 : 0 }}
                    transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                  />
                </button>
              </div>
            </div>

            {(!writeEvents || !modifyEvents) && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-3 bg-orange-50 rounded-xl p-4 border-2 border-orange-300"
                role="alert"
              >
                <div className="flex items-start gap-3">
                  <AlertTriangle className="w-5 h-5 text-orange-700 shrink-0 mt-0.5" aria-hidden="true" />
                  <div>
                    <h4 className="text-sm font-semibold text-orange-900 mb-1">Limited functionality</h4>
                    <p className="text-sm text-orange-800">
                      Some features may not work properly with these permissions disabled.
                    </p>
                  </div>
                </div>
              </motion.div>
            )}
          </section>

          {/* Save Button */}
          <button
            onClick={onClose}
            className="w-full px-6 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-md hover:from-blue-700 hover:to-purple-700 hover:shadow-lg hover:scale-105 transition-all focus:outline-none focus:ring-4 focus:ring-blue-300"
          >
            Save changes
          </button>
        </div>
      </motion.div>

      {/* Disconnect Confirmation Modal */}
      {showDisconnectConfirm && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="absolute inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center p-8"
          onClick={() => setShowDisconnectConfirm(false)}
        >
          <motion.div
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            onClick={(e) => e.stopPropagation()}
            className="glass-strong rounded-2xl p-8 max-w-md w-full border-2 border-red-300 shadow-xl"
            role="alertdialog"
            aria-labelledby="disconnect-confirm-title"
            aria-describedby="disconnect-confirm-description"
          >
            <div className="text-center mb-6">
              <div className="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4" aria-hidden="true">
                <AlertTriangle className="w-8 h-8 text-red-600" />
              </div>
              <h3 id="disconnect-confirm-title" className="text-xl text-gray-900 mb-2">Disconnect Google Calendar?</h3>
              <p id="disconnect-confirm-description" className="text-gray-600">
                You'll lose access to calendar sync features and imported events.
              </p>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setShowDisconnectConfirm(false)}
                className="flex-1 px-4 py-3 rounded-xl bg-white border-2 border-gray-400 text-gray-800 hover:border-gray-500 hover:bg-gray-50 transition-all focus:outline-none focus:ring-4 focus:ring-gray-300"
              >
                Cancel
              </button>
              <button
                onClick={handleDisconnect}
                className="flex-1 px-4 py-3 rounded-xl bg-gradient-to-r from-red-600 to-red-700 text-white shadow-md hover:from-red-700 hover:to-red-800 hover:shadow-lg transition-all focus:outline-none focus:ring-4 focus:ring-red-300"
              >
                Disconnect
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </motion.div>
  );
}
