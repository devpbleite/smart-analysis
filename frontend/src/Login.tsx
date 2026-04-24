import { useState } from 'react';

interface LoginProps {
  onLoginSuccess: (token: string) => void;
}

const Login: React.FC<LoginProps> = ({ onLoginSuccess }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const response = await fetch('http://localhost:8000/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Credenciais inválidas');
      }

      const data = await response.json();
      localStorage.setItem('insight_token', data.access_token);
      onLoginSuccess(data.access_token);
    } catch (err) {
      setError('Acesso negado. Usuário ou senha incorretos.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-chatBg font-sans">
      <div className="w-full max-w-md p-8 sm:p-10 bg-panel border mx-4 border-gray-700/50 rounded-2xl shadow-2xl backdrop-blur-md">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-2">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" fill="none" className="w-9 h-9 shrink-0">
              <rect width="32" height="32" rx="8" fill="#0e1117"/>
              <rect x="5" y="18" width="5" height="9" rx="1.5" fill="#77DD77"/>
              <rect x="13" y="12" width="5" height="15" rx="1.5" fill="#77DD77"/>
              <rect x="21" y="6" width="5" height="21" rx="1.5" fill="#77DD77"/>
              <polyline points="7.5,18 15.5,12 23.5,6" stroke="#89CFF0" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <h1 className="text-3xl font-bold text-white tracking-wide">InSight OS</h1>
          </div>
          <p className="text-gray-400 text-sm">Gestão Inteligente de Estoque</p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 text-red-400 text-sm rounded-xl text-center">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Credencial de Acesso</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full bg-chatBg border border-gray-700 text-white rounded-xl p-3 focus:outline-none focus:border-botMsg focus:ring-1 focus:ring-botMsg transition-all"
              placeholder="Digite seu usuário..."
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Chave de Segurança</label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-chatBg border border-gray-700 text-white rounded-xl p-3 pr-12 focus:outline-none focus:border-botMsg focus:ring-1 focus:ring-botMsg transition-all"
                placeholder="Digite sua senha..."
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-white transition-colors"
                title={showPassword ? "Ocultar senha" : "Mostrar senha"}
              >
                {showPassword ? (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                ) : (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>
                )}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading || !username || !password}
            className="w-full bg-gray-800 hover:bg-gray-700 text-white font-medium p-3.5 mt-2 rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <span className="animate-pulse">Decodificando Token...</span>
            ) : (
              <>
                <span>Entrar no Portal</span>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
              </>
            )}
          </button>
        </form>
        
        <div className="mt-8 text-center border-t border-gray-800 pt-6">
          <p className="text-xs text-gray-500">Acesso Restrito · Célula de Engenharia InSight</p>
        </div>
      </div>
    </div>
  );
};

export default Login;
