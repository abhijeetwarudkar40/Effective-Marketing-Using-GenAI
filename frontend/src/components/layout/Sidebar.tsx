import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  PieChart,
  Sparkles,
  Send,
  Palette,
  BarChart3,
  ShieldAlert,
  SendHorizontal,
  ChevronRight
} from 'lucide-react';

const navItems = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard, category: 'Core' },
  { name: 'Customer 360°', path: '/customers', icon: Users, category: 'Intelligence' },
  { name: 'Segments & Insights', path: '/segments', icon: PieChart, category: 'Intelligence' },
  { name: 'Product Recommendations', path: '/recommendations', icon: Sparkles, category: 'Intelligence' },
  { name: 'Campaign Studio', path: '/campaign-studio', icon: Send, category: 'Execution' },
  { name: 'Creative Studio', path: '/creative-studio', icon: Palette, category: 'Execution' },
  { name: 'Compliance & Approval', path: '/compliance', icon: ShieldAlert, category: 'Governance' },
  { name: 'Campaign Delivery', path: '/delivery', icon: SendHorizontal, category: 'Execution' },
  { name: 'Analytics & Performance', path: '/analytics', icon: BarChart3, category: 'Optimization' },
  { name: 'Governance & Audits', path: '/governance', icon: ShieldAlert, category: 'Governance' },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 bg-[#0A1628] border-r border-[#1A3A5C] flex flex-col justify-between h-[calc(100vh-4rem)] sticky top-16 select-none">
      <div className="py-4 px-3 space-y-1 overflow-y-auto">
        <div className="px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-[#00A896]">
          Navigation
        </div>
        
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-[#1A3A5C] text-white border-l-4 border-[#00A896] shadow-sm'
                    : 'text-gray-400 hover:text-white hover:bg-[#1A3A5C]/40'
                }`
              }
            >
              <div className="flex items-center space-x-3">
                <Icon className="w-4 h-4 text-[#00A896]" />
                <span>{item.name}</span>
              </div>
              <ChevronRight className="w-3.5 h-3.5 text-gray-500 opacity-50" />
            </NavLink>
          );
        })}
      </div>

      <div className="p-4 border-t border-[#1A3A5C] bg-[#070F1C]">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-semibold text-gray-400">Environment</span>
          <span className="text-[10px] bg-[#00A896]/20 text-[#00A896] px-2 py-0.5 rounded font-mono font-medium">Production</span>
        </div>
        <div className="text-[10px] text-gray-500 mt-2">
          Security: AES-256 PII Protected
        </div>
      </div>
    </aside>
  );
};
