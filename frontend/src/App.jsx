import ChatBox from "./components/ChatBox";

function App() {
  return (
    <div className="min-h-screen bg-slate-900 text-white flex items-center justify-center p-4 bg-[url('https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop')] bg-cover bg-center bg-no-repeat bg-blend-overlay bg-fixed">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm"></div>
      <div className="relative z-10 w-full max-w-4xl">
        <ChatBox />
      </div>
    </div>
  );
}

export default App;
