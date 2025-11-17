import { Link, useLocation } from "wouter";
import { 
  LayoutDashboard, 
  FileUp, 
  Receipt, 
  BarChart3, 
  FileText,
  Building2,
  LogOut
} from "lucide-react";
import { Button } from "./ui/button";

import { BACKEND_URL } from "@/config/api";
import logger from '@/utils/logger';

interface NavItem {
  path: string;
  label: string;
  icon: React.ReactNode;
}

const navItems: NavItem[] = [
  { path: "/", label: "Dashboard", icon: <LayoutDashboard className="w-5 h-5" /> },
  { path: "/companies", label: "Companies", icon: <Building2 className="w-5 h-5" /> },
  { path: "/accounts", label: "Chart of Accounts", icon: <FileText className="w-5 h-5" /> },
  { path: "/transactions", label: "Transactions", icon: <Receipt className="w-5 h-5" /> },
  { path: "/documents", label: "Documents", icon: <FileUp className="w-5 h-5" /> },
  { path: "/reports", label: "Reports", icon: <BarChart3 className="w-5 h-5" /> },
  { path: "/irs-forms", label: "IRS Forms", icon: <FileText className="w-5 h-5" /> },
];

export default function Sidebar() {
  const [location] = useLocation();

  const handleLogout = async () => {
    try {
      await fetch(`${BACKEND_URL}/api/auth/logout/`, {
        method: 'POST',
        credentials: 'include'
      });
      window.location.href = '/login';
    } catch (error) {
      logger.error('Logout failed', error);
    }
  };

  return (
    <div className="flex flex-col h-screen w-64 bg-bts-blue border-r border-bts-blue-c02">
      {/* Logo/Header - BTS Design System */}
      <div className="p-6 border-b border-bts-blue-c02">
        <div className="flex items-center gap-2">
          <Building2 className="w-8 h-8 text-bts-blue-505" />
          <div>
            <h1 className="font-semibold text-lg text-white">Orion Ledger</h1>
            <p className="text-xs text-bts-gray-light">US Accounting System</p>
          </div>
        </div>
      </div>

      {/* Navigation - BTS Design System */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          const isActive = location === item.path || 
                          (item.path !== "/" && item.path !== "/dashboard" && location.startsWith(item.path));
          
          return (
            <Link key={item.path} href={item.path}>
              <a
                className={`
                  flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200
                  font-medium text-sm
                  ${isActive 
                    ? 'bg-bts-blue-highlight text-white shadow-md' 
                    : 'text-bts-gray-light hover:bg-bts-blue-c02 hover:text-white'
                  }
                `}
              >
                {item.icon}
                <span>{item.label}</span>
              </a>
            </Link>
          );
        })}
      </nav>

      {/* Footer - BTS Design System */}
      <div className="p-4 border-t border-bts-blue-c02">
        <Button
          variant="ghost"
          className="w-full justify-start text-bts-gray-light hover:bg-bts-blue-c02 hover:text-white transition-colors"
          onClick={handleLogout}
        >
          <LogOut className="w-5 h-5 mr-3" />
          Logout
        </Button>
      </div>
    </div>
  );
}
