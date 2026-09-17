import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingSpinnerProps {
  message?: string;
  className?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  message = 'Loading data...',
  className = 'py-16',
}) => {
  return (
    <div className={`flex flex-col items-center justify-center space-y-3 ${className}`}>
      <Loader2 className="w-8 h-8 text-[#00A896] animate-spin" />
      <p className="text-sm font-medium text-gray-500">{message}</p>
    </div>
  );
};
