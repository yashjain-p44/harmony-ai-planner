import { createContext, useContext, useState } from 'react';

const PlanContext = createContext(null);

export const usePlan = () => {
  const context = useContext(PlanContext);
  if (!context) {
    throw new Error('usePlan must be used within PlanProvider');
  }
  return context;
};

const initialRequirements = {
  goal: '',
  timeCommitment: '',
  preferredDays: [],
  fixedCommitments: '',
  energyPreference: null, // 'morning' | 'evening' | null
};

export const PlanProvider = ({ children }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [requirements, setRequirements] = useState(initialRequirements);

  const openSidebar = () => setIsOpen(true);
  const closeSidebar = () => setIsOpen(false);
  const toggleSidebar = () => setIsOpen((prev) => !prev);

  const updateRequirement = (field, value) => {
    setRequirements((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const updatePreferredDays = (day, checked) => {
    setRequirements((prev) => {
      const days = prev.preferredDays || [];
      if (checked) {
        return {
          ...prev,
          preferredDays: [...days, day],
        };
      } else {
        return {
          ...prev,
          preferredDays: days.filter((d) => d !== day),
        };
      }
    });
  };

  const resetRequirements = () => {
    setRequirements(initialRequirements);
  };

  const value = {
    isOpen,
    requirements,
    openSidebar,
    closeSidebar,
    toggleSidebar,
    updateRequirement,
    updatePreferredDays,
    resetRequirements,
  };

  return <PlanContext.Provider value={value}>{children}</PlanContext.Provider>;
};
