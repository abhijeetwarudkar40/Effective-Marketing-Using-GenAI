import React from 'react';
import { LucideIcon } from 'lucide-react';

interface KPICardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: LucideIcon;
  trend?: {
    value: string;
    isPositive?: boolean;
  };
  accentColor?: string;
}

export const KPICard: React.FC<KPICardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  accentColor = '#00A896',
}) => {
  return (
    <div className="bg-white rounded-xl p-5 border border-gray-200/80 shadow-xs hover:shadow-sm transition-all duration-200 relative overflow-hidden flex flex-col justify-between">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-gray-500">{title}</p>
          <h3 className="text-2xl font-bold text-[#0A1628] mt-1 tracking-tight">{value}</h3>
        </div>
        {Icon && (
          <div
            className="w-10 h-10 rounded-lg flex items-center justify-center text-white"
            style={{ backgroundColor: accentColor }}
          >
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>

      {(subtitle || trend) && (
        <div className="mt-3 pt-3 border-t border-gray-100 flex items-center justify-between text-xs">
          {subtitle && <span className="text-gray-500">{subtitle}</span>}
          {trend && (
            <span
              className={`font-semibold flex items-center space-x-1 ${
                trend.isPositive ? 'text-[#2E7D32]' : 'text-[#C53030]'
              }`}
            >
              <span>{trend.isPositive ? '↑' : '↓'}</span>
              <span>{trend.value}</span>
            </span>
          )}
        </div>
      )}
    </div>
  );
};
