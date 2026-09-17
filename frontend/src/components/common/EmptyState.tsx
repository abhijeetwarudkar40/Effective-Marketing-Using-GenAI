import React from 'react';
import { Inbox } from 'lucide-react';

interface EmptyStateProps {
  title?: string;
  description?: string;
  action?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title = 'No records found',
  description = 'There is currently no data to display.',
  action,
}) => {
  return (
    <div className="bg-white rounded-xl p-10 border border-gray-200 text-center flex flex-col items-center justify-center my-6">
      <div className="w-12 h-12 rounded-full bg-gray-50 flex items-center justify-center text-gray-400 mb-3 border border-gray-100">
        <Inbox className="w-6 h-6" />
      </div>
      <h3 className="text-base font-semibold text-gray-800">{title}</h3>
      <p className="text-xs text-gray-500 max-w-sm mt-1 mb-4">{description}</p>
      {action}
    </div>
  );
};
