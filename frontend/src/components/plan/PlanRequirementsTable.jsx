import { usePlan } from '../../context/PlanContext';

const DAYS_OF_WEEK = [
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday',
  'Sunday',
];

const PlanRequirementsTable = () => {
  const { requirements, updateRequirement, updatePreferredDays } = usePlan();

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold text-primary mb-6">Plan Requirements</h2>

      <div className="space-y-5">
        {/* Goal / Focus Area */}
        <div>
          <label
            htmlFor="goal"
            className="block text-sm font-medium text-primary mb-2"
          >
            Goal / Focus Area
          </label>
          <input
            id="goal"
            type="text"
            value={requirements.goal}
            onChange={(e) => updateRequirement('goal', e.target.value)}
            placeholder="e.g., Learn React, Build projects"
            className="w-full px-4 py-2 bg-charcoal border border-subtle rounded-lg text-primary placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-accent-purple focus:border-transparent transition-all"
          />
        </div>

        {/* Time Commitment */}
        <div>
          <label
            htmlFor="timeCommitment"
            className="block text-sm font-medium text-primary mb-2"
          >
            Time Commitment (hours/week)
          </label>
          <input
            id="timeCommitment"
            type="number"
            min="0"
            value={requirements.timeCommitment}
            onChange={(e) => updateRequirement('timeCommitment', e.target.value)}
            placeholder="e.g., 10"
            className="w-full px-4 py-2 bg-charcoal border border-subtle rounded-lg text-primary placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-accent-purple focus:border-transparent transition-all"
          />
        </div>

        {/* Preferred Days */}
        <div>
          <label className="block text-sm font-medium text-primary mb-3">
            Preferred Days
          </label>
          <div className="grid grid-cols-2 gap-2">
            {DAYS_OF_WEEK.map((day) => (
              <label
                key={day}
                className="flex items-center gap-2 p-2 rounded-lg hover:bg-charcoal cursor-pointer transition-colors"
              >
                <input
                  type="checkbox"
                  checked={requirements.preferredDays?.includes(day) || false}
                  onChange={(e) => updatePreferredDays(day, e.target.checked)}
                  className="w-4 h-4 text-accent-purple bg-charcoal border-subtle rounded focus:ring-accent-purple focus:ring-2"
                />
                <span className="text-sm text-secondary">{day}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Fixed Commitments */}
        <div>
          <label
            htmlFor="fixedCommitments"
            className="block text-sm font-medium text-primary mb-2"
          >
            Fixed Commitments
          </label>
          <textarea
            id="fixedCommitments"
            value={requirements.fixedCommitments}
            onChange={(e) => updateRequirement('fixedCommitments', e.target.value)}
            placeholder="e.g., Work 9-5, Monday to Friday"
            rows={3}
            className="w-full px-4 py-2 bg-charcoal border border-subtle rounded-lg text-primary placeholder-gray-500 resize-none focus:outline-none focus:ring-2 focus:ring-accent-purple focus:border-transparent transition-all"
          />
        </div>

        {/* Energy Preference */}
        <div>
          <label className="block text-sm font-medium text-primary mb-3">
            Energy Preference
          </label>
          <div className="flex gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="energyPreference"
                value="morning"
                checked={requirements.energyPreference === 'morning'}
                onChange={(e) => updateRequirement('energyPreference', e.target.value)}
                className="w-4 h-4 text-accent-purple bg-charcoal border-subtle focus:ring-accent-purple focus:ring-2"
              />
              <span className="text-sm text-secondary">Morning</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="energyPreference"
                value="evening"
                checked={requirements.energyPreference === 'evening'}
                onChange={(e) => updateRequirement('energyPreference', e.target.value)}
                className="w-4 h-4 text-accent-purple bg-charcoal border-subtle focus:ring-accent-purple focus:ring-2"
              />
              <span className="text-sm text-secondary">Evening</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="energyPreference"
                value=""
                checked={!requirements.energyPreference}
                onChange={() => updateRequirement('energyPreference', null)}
                className="w-4 h-4 text-accent-purple bg-charcoal border-subtle focus:ring-accent-purple focus:ring-2"
              />
              <span className="text-sm text-secondary">No preference</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PlanRequirementsTable;
