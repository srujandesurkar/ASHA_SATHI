import React from 'react';
import { AlertTriangle, ChevronRight, Phone, ShieldAlert, ArrowUpRight } from 'lucide-react';

interface ReferralAlertsListProps {
  urgentTasks: Array<{
    id: string;
    beneficiary_id: string;
    beneficiary_name?: string;
    title: string;
    description?: string;
    due_date: string;
    priority: string;
  }>;
  onSelectBeneficiary?: (benId: string) => void;
}

export const ReferralAlertsList: React.FC<ReferralAlertsListProps> = ({
  urgentTasks,
  onSelectBeneficiary,
}) => {
  if (!urgentTasks || urgentTasks.length === 0) {
    return (
      <div className="bg-white border border-slate-200 rounded-2xl p-4 sm:p-5 shadow-sm">
        <div className="flex items-center space-x-2 text-slate-800 font-bold mb-2">
          <ShieldAlert className="w-5 h-5 text-emerald-600" />
          <h3 className="text-sm font-bold">Active Danger Sign Escalate Board</h3>
        </div>
        <p className="text-xs text-slate-500">
          No active emergency danger referrals pending in your catchment area.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white border-2 border-red-200 rounded-2xl p-4 sm:p-5 shadow-md">
      <div className="flex items-center justify-between pb-3 border-b border-red-100">
        <div className="flex items-center space-x-2">
          <span className="p-1.5 rounded-lg bg-red-100 text-red-700 animate-pulse">
            <AlertTriangle className="w-5 h-5" />
          </span>
          <div>
            <h3 className="text-sm font-extrabold text-red-950 tracking-tight">
              High-Risk PHC Referral Watchlist ({urgentTasks.length})
            </h3>
            <span className="text-[11px] text-red-600 font-semibold">
              MoHFW Protocol: Requires 24-hr field follow-up
            </span>
          </div>
        </div>
      </div>

      <div className="mt-3 divide-y divide-red-50">
        {urgentTasks.map((task) => (
          <div
            key={task.id}
            className="py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2 hover:bg-red-50/50 p-2 rounded-xl transition"
          >
            <div>
              <div className="flex items-center space-x-2">
                <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-red-600 text-white">
                  EMERGENCY
                </span>
                <span className="text-xs font-bold text-slate-900">
                  {task.beneficiary_id} - {task.beneficiary_name || 'Patient'}
                </span>
              </div>
              <p className="text-xs text-slate-700 font-medium mt-1">
                {task.title}
              </p>
              {task.description && (
                <p className="text-[11px] text-slate-500 mt-0.5 line-clamp-1">
                  {task.description}
                </p>
              )}
            </div>

            <div className="flex items-center space-x-2 shrink-0">
              <span className="text-[11px] font-semibold text-slate-500">
                Due: {task.due_date}
              </span>
              {onSelectBeneficiary && (
                <button
                  onClick={() => onSelectBeneficiary(task.beneficiary_id)}
                  className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-red-100 text-red-800 hover:bg-red-200 transition flex items-center space-x-1"
                >
                  <span>Review</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
