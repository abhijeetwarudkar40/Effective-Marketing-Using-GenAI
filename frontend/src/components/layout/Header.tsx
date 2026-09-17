import React from 'react';
import { ShieldCheck, Bell, UserCircle, Activity } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="h-16 bg-[#0A1628] border-b border-[#1A3A5C] flex items-center justify-between px-6 z-20 text-white sticky top-0">
      <div className="flex items-center space-x-3">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-[#00A896] to-[#2C9C8F] flex items-center justify-center shadow-md shadow-[#00A896]/20">
          <ShieldCheck className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <span className="font-bold text-lg tracking-tight text-white">BANKWISE <span className="text-[#00A896]">AI</span></span>
            <span className="text-[10px] uppercase font-semibold tracking-wider bg-[#1A3A5C] text-[#00A896] px-2 py-0.5 rounded border border-[#00A896]/30">
              Enterprise Intelligence
            </span>
          </div>
          <p className="text-[11px] text-[#A0AEC0] hidden sm:block">AI-Powered Banking Marketing Intelligence Platform</p>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <div className="hidden md:flex items-center space-x-2 bg-[#1A3A5C]/60 px-3 py-1.5 rounded-full border border-[#2C5F8A]/40 text-xs">
          <span className="w-2 h-2 rounded-full bg-[#00A896] animate-pulse"></span>
          <span className="text-gray-300 font-medium">Core AI Engine:</span>
          <span className="text-[#00A896] font-semibold">Gemini 3.6 Flash Active</span>
        </div>

        <div className="flex items-center space-x-2 border-l border-[#1A3A5C] pl-4">
          <button className="p-2 rounded-lg hover:bg-[#1A3A5C] text-gray-300 hover:text-white transition-colors relative" title="Notifications">
            <Bell className="w-4 h-4" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-[#C9A84C] rounded-full"></span>
          </button>
          
          <div className="flex items-center space-x-2 pl-2">
            <div className="w-8 h-8 rounded-full bg-[#1A3A5C] border border-[#C9A84C]/40 flex items-center justify-center text-[#C9A84C] font-semibold text-xs">
              BW
            </div>
            <div className="hidden lg:block text-left">
              <div className="text-xs font-semibold text-gray-200">Marketing Lead</div>
              <div className="text-[10px] text-gray-400">Enterprise Admin</div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
