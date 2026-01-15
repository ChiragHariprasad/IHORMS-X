import React from 'react';
import { cn } from '@/lib/utils';

type StatusType = 
  | 'pending'
  | 'confirmed'
  | 'completed'
  | 'cancelled'
  | 'active'
  | 'inactive'
  | 'approved'
  | 'rejected'
  | 'in_progress'
  | 'scheduled';

interface StatusBadgeProps {
  status: string;
  className?: string;
}

const statusConfig: Record<string, { label: string; className: string }> = {
  pending: { label: 'Pending', className: 'status-pending' },
  confirmed: { label: 'Confirmed', className: 'status-confirmed' },
  completed: { label: 'Completed', className: 'status-completed' },
  cancelled: { label: 'Cancelled', className: 'status-cancelled' },
  active: { label: 'Active', className: 'status-active' },
  inactive: { label: 'Inactive', className: 'status-inactive' },
  approved: { label: 'Approved', className: 'status-completed' },
  rejected: { label: 'Rejected', className: 'status-cancelled' },
  in_progress: { label: 'In Progress', className: 'status-confirmed' },
  scheduled: { label: 'Scheduled', className: 'status-confirmed' },
};

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className }) => {
  const normalizedStatus = status.toLowerCase().replace(/\s+/g, '_');
  const config = statusConfig[normalizedStatus] || {
    label: status,
    className: 'status-inactive',
  };

  return (
    <span className={cn('status-badge', config.className, className)}>
      {config.label}
    </span>
  );
};
