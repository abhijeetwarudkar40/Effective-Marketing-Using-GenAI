import React from 'react';

type BadgeVariant = 'success' | 'warning' | 'danger' | 'info' | 'neutral' | 'gold' | 'teal';

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ children, variant = 'neutral', className = '' }) => {
  const variantStyles: Record<BadgeVariant, string> = {
    success: 'bg-[#2E7D32]/10 text-[#2E7D32] border-[#2E7D32]/20',
    warning: 'bg-[#E65100]/10 text-[#E65100] border-[#E65100]/20',
    danger: 'bg-[#C53030]/10 text-[#C53030] border-[#C53030]/20',
    info: 'bg-[#0D47A1]/10 text-[#0D47A1] border-[#0D47A1]/20',
    neutral: 'bg-gray-100 text-gray-700 border-gray-200',
    gold: 'bg-[#C9A84C]/15 text-[#8D6B00] border-[#C9A84C]/30',
    teal: 'bg-[#00A896]/15 text-[#007A6C] border-[#00A896]/30',
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${variantStyles[variant]} ${className}`}
    >
      {children}
    </span>
  );
};
