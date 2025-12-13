import { usePlan } from '../../context/PlanContext';
import TopBar from './TopBar';
import ChatWindow from '../chat/ChatWindow';
import PlanSidebar from '../plan/PlanSidebar';

const AppLayout = () => {
  const { isOpen } = usePlan();

  return (
    <div className="flex flex-col h-screen bg-charcoal overflow-hidden">
      <TopBar />
      
      <div className="flex-1 flex overflow-hidden relative">
        {/* Main Chat Area */}
        <main className="flex-1 flex flex-col overflow-hidden min-w-0">
          <ChatWindow />
        </main>

        {/* Plan Sidebar */}
        <PlanSidebar />
      </div>
    </div>
  );
};

export default AppLayout;
