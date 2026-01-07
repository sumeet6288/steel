import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { LayoutDashboard, FolderKanban, Settings, LogOut, FileText } from 'lucide-react';
import { removeAuthToken, removeUser, getUser } from '../../lib/auth';
import { Button } from '../ui/button';
import { toast } from 'sonner';

export const Sidebar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const user = getUser();

  const handleLogout = () => {
    removeAuthToken();
    removeUser();
    toast.success('Logged out successfully');
    navigate('/login');
  };

  const menuItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/projects', icon: FolderKanban, label: 'Projects' },
    { path: '/audit', icon: FileText, label: 'Audit Log' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col" data-testid="sidebar">
      <div className="p-6 border-b border-slate-100">
        <h1 className="text-xl font-heading font-bold text-slate-900" data-testid="app-title">
          SteelConnect AI
        </h1>
        <p className="text-xs text-slate-500 mt-1">AISC Design Assist</p>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname.startsWith(item.path);
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-3 py-2 rounded-sm text-sm font-medium ${
                isActive
                  ? 'bg-slate-100 text-slate-900'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
              }`}
              data-testid={`nav-${item.label.toLowerCase().replace(' ', '-')}`}
            >
              <Icon size={18} strokeWidth={1.5} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-slate-100">
        <div className="mb-3">
          <p className="text-sm font-medium text-slate-900">{user?.full_name}</p>
          <p className="text-xs text-slate-500">{user?.email}</p>
        </div>
        <Button
          onClick={handleLogout}
          variant="ghost"
          className="w-full justify-start text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-sm"
          data-testid="logout-button"
        >
          <LogOut size={18} strokeWidth={1.5} className="mr-2" />
          Log Out
        </Button>
      </div>
    </aside>
  );
};