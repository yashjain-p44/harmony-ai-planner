import { useEffect } from 'react';
import { usePlan } from '../../context/PlanContext';
import PlanRequirementsTable from './PlanRequirementsTable';

const PlanSidebar = () => {
  const { isOpen, closeSidebar } = usePlan();

  // Prevent body scroll when sidebar is open on mobile
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  // Handle escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && isOpen) {
        closeSidebar();
      }
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, closeSidebar]);

  return (
    <>
      {/* Backdrop for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden transition-opacity"
          onClick={closeSidebar}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed md:relative
          top-0 right-0
          h-full w-full md:w-96
          bg-charcoal-light border-l border-subtle
          z-50 md:z-auto
          transform transition-transform duration-300 ease-in-out
          shadow-xl md:shadow-none
          ${isOpen ? 'translate-x-0' : 'translate-x-full'}
          ${isOpen ? 'block' : 'hidden'}
          overflow-y-auto
        `}
      >
        <div className="sticky top-0 bg-charcoal-light border-b border-subtle px-6 py-4 flex items-center justify-between z-10">
          <h2 className="text-lg font-semibold text-primary">Plan Requirements</h2>
          <button
            onClick={closeSidebar}
            className="p-2 text-secondary hover:text-primary transition-colors rounded-md hover:bg-charcoal focus:outline-none focus:ring-2 focus:ring-accent-purple focus:ring-offset-2 focus:ring-offset-charcoal-light"
            aria-label="Close sidebar"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <div className="p-6">
          <PlanRequirementsTable />
        </div>
      </aside>

    </>
  );
};

export default PlanSidebar;
