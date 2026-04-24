import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import Login from './Login';
import './index.css';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

const UserIcon = () => (
  <svg fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" className="w-5 h-5">
    <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
  </svg>
);

const BotIcon = () => (
  <svg fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" className="w-5 h-5">
    <path strokeLinecap="round" strokeLinejoin="round" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM10 11h.01M14 11h.01M9 15h6"></path>
  </svg>
);

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(!!localStorage.getItem('insight_token'));

  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Olá! Sou o assistente responsável pela inteligência do estoque. Como posso ajudar sobre o estoque hoje?' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const endOfMessagesRef = useRef<HTMLDivElement>(null);

  const handleClearChat = () => {
    setMessages([
      { role: 'assistant', content: 'Mensagens limpas! Qual a próxima análise logística que vamos realizar?' }
    ]);
  };

  const handleLogout = () => {
    localStorage.removeItem('insight_token');
    setIsAuthenticated(false);
  };

  const scrollToBottom = () => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMsg = input.trim();
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setInput('');

    setTimeout(async () => {
      setIsLoading(true);

      try {
        const response = await fetch('http://localhost:8000/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('insight_token')}`
          },
          body: JSON.stringify({ message: userMsg }),
        });
        
        if (!response.ok) throw new Error('API Error');
        const data = await response.json();
        
        setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
      } catch (e) {
        setMessages(prev => [...prev, { role: 'assistant', content: '❌ Erro de conexão com o InSight API. Verifique se o backend está rodando na porta 8000.' }]);
      } finally {
        setIsLoading(false);
      }
    }, 600);
  };

  const handleMenuClick = (text: string) => {
    setInput(text);
    setMenuOpen(false);
  };

  if (!isAuthenticated) {
    return <Login onLoginSuccess={() => setIsAuthenticated(true)} />;
  }

  return (
    <div className="flex h-screen bg-chatBg text-gray-100 overflow-hidden font-sans">
      
      {/* Floating Sidebar / Menu Overlay para Mobile */}
      <div 
        className={`fixed inset-y-0 left-0 z-50 w-[80vw] sm:w-72 bg-panel shadow-2xl transform transition-transform duration-300 ease-in-out ${menuOpen ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0 md:static border-r border-gray-700`}
      >
        <div className="flex flex-col h-full bg-panel">
          <div className="p-6 pt-10 pb-6 flex flex-col justify-center items-start">
             <div className="flex justify-between items-center w-full">
                <div className="flex items-center gap-2"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" fill="none" className="w-7 h-7 shrink-0"><rect width="32" height="32" rx="8" fill="#0e1117"/><rect x="5" y="18" width="5" height="9" rx="1.5" fill="#77DD77"/><rect x="13" y="12" width="5" height="15" rx="1.5" fill="#77DD77"/><rect x="21" y="6" width="5" height="21" rx="1.5" fill="#77DD77"/><polyline points="7.5,18 15.5,12 23.5,6" stroke="#89CFF0" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg><h1 className="text-2xl font-bold text-white tracking-wide">InSight</h1></div>
                <button className="md:hidden text-gray-400 hover:text-white" onClick={() => setMenuOpen(false)}>
                  ✕
                </button>
             </div>
             <p className="text-sm text-gray-400 mt-1">Gestão Inteligente de Estoque</p>
          </div>
          <div className="flex-1 overflow-y-auto px-4 pb-4 space-y-2">
            <div className="text-xs font-semibold text-gray-400 uppercase tracking-widest mt-4 mb-3">Guias Sugeridos</div>
            <button onClick={() => handleMenuClick("Valor total do estoque")} className="text-left w-full hover:bg-gray-700/50 rounded-lg p-3 text-sm transition-colors text-gray-200">💰 Valor total do estoque</button>
            <button onClick={() => handleMenuClick("Quantidade de skus do estoque")} className="text-left w-full hover:bg-gray-700/50 rounded-lg p-3 text-sm transition-colors text-gray-200">📦 Quantidade de skus do estoque</button>
            <button onClick={() => handleMenuClick("Quantidade total de itens")} className="text-left w-full hover:bg-gray-700/50 rounded-lg p-3 text-sm transition-colors text-gray-200">📋 Quantidade total de itens</button>
            <button onClick={() => handleMenuClick("Verificar validade dos produtos a vencer na faixa vermelha")} className="text-left w-full hover:bg-gray-700/50 rounded-lg p-3 text-sm transition-colors text-gray-200">🚨 Verificar validade na faixa vermelha</button>
            <button onClick={() => handleMenuClick("Quais os 10 produtos mais vendidos e os valores totais das vendas")} className="text-left w-full hover:bg-gray-700/50 rounded-lg p-3 text-sm transition-colors text-gray-200">⭐ Top 10 Produtos mais vendidos</button>
            <button onClick={() => handleMenuClick("Qual faturamento no primeiro trimestre de 2025")} className="text-left w-full hover:bg-gray-700/50 rounded-lg p-3 text-sm transition-colors text-gray-200">📈 Faturamento 1º Trimestre (2025)</button>
          </div>
          <div className="p-4 text-xs text-gray-500 text-center">
            InSight OS — 2.0
          </div>
        </div>
      </div>

      {/* Área Principal de Chat */}
      <div className="flex-1 flex flex-col min-w-0 bg-chatBg relative">
        {/* Header/Navbar Global */}
        <header className="flex items-center justify-between p-3 sm:p-4 bg-chatBg/90 sticky top-0 z-10 border-b border-gray-800/80 backdrop-blur-md">
          <div className="flex items-center">
            <button 
              onClick={() => setMenuOpen(true)}
              className="md:hidden p-2 mr-2 rounded-md text-gray-300 hover:text-white"
            >
              <svg className="w-5 h-5 sm:w-6 sm:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /></svg>
            </button>
            <span className="md:hidden flex items-center gap-1.5 font-semibold text-white">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" fill="none" className="w-5 h-5 shrink-0">
                <rect width="32" height="32" rx="8" fill="#0e1117"/>
                <rect x="5" y="18" width="5" height="9" rx="1.5" fill="#77DD77"/>
                <rect x="13" y="12" width="5" height="15" rx="1.5" fill="#77DD77"/>
                <rect x="21" y="6" width="5" height="21" rx="1.5" fill="#77DD77"/>
                <polyline points="7.5,18 15.5,12 23.5,6" stroke="#89CFF0" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              InSight OS
            </span>
          </div>
          
          {/* Action Buttons (Limpar & Logout) */}
          <div className="flex items-center gap-2 sm:gap-3 ml-auto">
             <button
               onClick={handleClearChat}
               disabled={messages.length <= 1}
               className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm transition-colors ${
                 messages.length <= 1 
                 ? 'text-gray-600 cursor-not-allowed opacity-50' 
                 : 'text-gray-400 hover:text-white hover:bg-gray-800'
               }`}
               title="Limpar memória do chat"
             >
               <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
               <span className="hidden sm:inline font-medium">Limpar chat</span>
             </button>
             <button
               onClick={handleLogout}
               className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm text-red-500 hover:text-red-400 hover:bg-red-500/10 transition-colors"
               title="Sair do sistema"
             >
               <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
               <span className="hidden sm:inline font-medium">Sair</span>
             </button>
          </div>
        </header>

        {/* Histórico Chat */}
        <main className="flex-1 overflow-y-auto px-2 py-4 sm:px-6 md:px-20 lg:px-40 space-y-4 sm:space-y-6">
          {messages.map((msg, index) => (
            <div key={index} className="flex items-center gap-3 sm:gap-5 p-4 sm:p-6 rounded-2xl bg-panel/40 border border-gray-700/30 shadow-sm">
              <div className={`w-8 h-8 rounded-md flex items-center justify-center shrink-0 border-2 bg-chatBg shadow-sm 
                ${msg.role === 'user' ? 'text-[#89CFF0] border-[#89CFF0]' : 'text-[#77DD77] border-[#77DD77]'}`}>
                {msg.role === 'user' ? <UserIcon /> : <BotIcon />}
              </div>
              <div className="flex-1 text-sm md:text-base leading-relaxed text-gray-100 min-w-0 overflow-x-auto">
                <div className="prose prose-sm md:prose-base prose-invert prose-p:leading-relaxed prose-pre:bg-gray-800 prose-ul:list-disc prose-ol:list-decimal max-w-none break-words">
                  <ReactMarkdown>
                    {msg.content}
                  </ReactMarkdown>
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex items-center gap-3 sm:gap-5 p-4 sm:p-6 rounded-2xl bg-panel/40 border border-gray-700/30 shadow-sm">
               <div className="w-8 h-8 md:w-9 md:h-9 rounded-md flex items-center justify-center shrink-0 border-2 bg-chatBg shadow-sm text-[#77DD77] border-[#77DD77]">
                <BotIcon />
              </div>
              <div className="flex-1 text-sm md:text-base text-gray-400 mt-1 sm:mt-1.5 min-w-0">
                <span className="animate-pulse">Analisando inteligência baseada em DuckDB...</span>
              </div>
            </div>
          )}
          <div ref={endOfMessagesRef} className="h-4" />
        </main>

        {/* Input Bar */}
        <div className="px-2 pb-4 pt-2 sm:p-4 lg:px-40 bg-chatBg relative shrink-0">
          <div className="relative max-w-4xl mx-auto flex items-center gap-1 sm:gap-2 bg-panel rounded-xl border border-gray-700/50 shadow-sm focus-within:border-botMsg focus-within:ring-1 focus-within:ring-botMsg transition-all pr-1">
            <textarea
              ref={(el) => {
                if (el) {
                  el.style.height = 'auto';
                  el.style.height = Math.min(el.scrollHeight, 160) + 'px';
                }
              }}
              className="flex-1 bg-transparent text-white text-sm py-3 px-4 sm:px-5 focus:outline-none resize-none overflow-y-auto leading-relaxed"
              rows={1}
              placeholder="Digite aqui sua dúvida de negócio..."
              value={input}
              onChange={(e) => {
                setInput(e.target.value);
                e.target.style.height = 'auto';
                e.target.style.height = Math.min(e.target.scrollHeight, 160) + 'px';
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
            />
            <button 
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
              className="p-2 sm:p-2.5 rounded-lg text-gray-400 hover:text-botMsg hover:bg-gray-800 transition-all disabled:opacity-30 disabled:cursor-not-allowed shrink-0"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </button>
          </div>
          <div className="text-center text-xs text-gray-500 mt-3 pb-2">
            O Painel InSight pode cometer erros. Consulte os artefatos de dados sensíveis.
          </div>
        </div>

      </div>
    </div>
  );
}

export default App;
