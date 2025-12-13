import { ChatProvider } from './context/ChatContext';
import { PlanProvider } from './context/PlanContext';
import AppLayout from './components/layout/AppLayout';

function App() {
  return (
    <ChatProvider>
      <PlanProvider>
        <AppLayout />
      </PlanProvider>
    </ChatProvider>
  );
}

export default App;
