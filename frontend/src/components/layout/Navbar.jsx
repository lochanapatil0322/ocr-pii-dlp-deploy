import { useAuth } from "../../context/AuthContext";
import { useNavigate } from "react-router-dom";

function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const initials = (user?.email || 'A')
    .split('@')[0]
    .split(/[._\- ]+/)
    .map((part) => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase() || 'A';

  return (
    <div className="sticky top-0 z-20 bg-slate-900/80 backdrop-blur border-b border-slate-800/70 px-4 sm:px-6 lg:px-8 py-3.5 flex flex-wrap items-center gap-3">

      <div className="min-w-0">
        <h1 className="font-display text-lg md:text-2xl font-semibold text-white truncate">
          AI Data Security Dashboard
        </h1>
        <p className="hidden sm:block text-[11px] tracking-wide text-slate-500">
          OCR Data Loss Prevention · Compliance &amp; Governance Console
        </p>
      </div>

      <div className="ml-auto flex items-center gap-3">
        <div className="flex items-center gap-2.5 rounded-xl border border-slate-700/60 bg-slate-800/50 py-1.5 pl-1.5 pr-3">
          <span className="w-8 h-8 shrink-0 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center text-xs font-bold text-white">
            {initials}
          </span>
          <div className="min-w-0 hidden md:block">
            <p className="text-xs font-semibold text-white leading-tight truncate max-w-[180px]">
              {user?.email || 'Admin'}
            </p>
            <p className="text-[10px] text-slate-500 leading-tight">
              {user?.role ? user.role.charAt(0).toUpperCase() + user.role.slice(1) : 'User'}
            </p>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="shrink-0 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors border border-slate-700/60"
        >
          Logout
        </button>
      </div>

    </div>
  );
}

export default Navbar;