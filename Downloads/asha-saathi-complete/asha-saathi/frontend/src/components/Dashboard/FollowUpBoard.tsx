import React, { useState } from 'react';
import { CheckCircle2, Clock, AlertCircle, Calendar, CheckSquare, Square } from 'lucide-react';
import { FollowUpTask } from '../../types/followUp';

interface FollowUpBoardProps {
  tasks: FollowUpTask[];
  onCompleteTask: (taskId: string) => void;
}

export const FollowUpBoard: React.FC<FollowUpBoardProps> = ({
  tasks,
  onCompleteTask,
}) => {
  const [filter, setFilter] = useState<'ALL' | 'EMERGENCY' | 'PENDING' | 'COMPLETED'>('ALL');

  const filteredTasks = tasks.filter((t) => {
    if (filter === 'EMERGENCY') return t.priority === 'EMERGENCY' && t.status === 'PENDING';
    if (filter === 'PENDING') return t.status === 'PENDING';
    if (filter === 'COMPLETED') return t.status === 'COMPLETED';
    return true;
  });

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-4 sm:p-5 shadow-sm my-4">
      {/* Header and Filter Tabs */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-100 gap-2">
        <div className="flex items-center space-x-2">
          <Calendar className="w-5 h-5 text-teal-600" />
          <h3 className="font-bold text-slate-900 text-sm sm:text-base">
            ASHA Follow-Up Task Register (Module 5)
          </h3>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center space-x-1 bg-slate-100 p-1 rounded-xl text-xs font-semibold">
          <button
            onClick={() => setFilter('ALL')}
            className={`px-3 py-1 rounded-lg transition ${
              filter === 'ALL' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            All ({tasks.length})
          </button>
          <button
            onClick={() => setFilter('PENDING')}
            className={`px-3 py-1 rounded-lg transition ${
              filter === 'PENDING' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            Pending
          </button>
          <button
            onClick={() => setFilter('EMERGENCY')}
            className={`px-3 py-1 rounded-lg transition ${
              filter === 'EMERGENCY' ? 'bg-red-600 text-white shadow-sm' : 'text-red-600 hover:text-red-800'
            }`}
          >
            Urgent
          </button>
          <button
            onClick={() => setFilter('COMPLETED')}
            className={`px-3 py-1 rounded-lg transition ${
              filter === 'COMPLETED' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            Completed
          </button>
        </div>
      </div>

      {/* Task List */}
      <div className="mt-3 divide-y divide-slate-100">
        {filteredTasks.length === 0 ? (
          <div className="py-6 text-center text-xs text-slate-400">
            No follow-up tasks match this filter.
          </div>
        ) : (
          filteredTasks.map((task) => {
            const isEmergency = task.priority === 'EMERGENCY';
            const isCompleted = task.status === 'COMPLETED';

            return (
              <div
                key={task.id}
                className="py-3 flex items-start justify-between gap-3 hover:bg-slate-50/70 p-2 rounded-xl transition"
              >
                <div className="flex items-start space-x-3">
                  <button
                    onClick={() => !isCompleted && onCompleteTask(task.id)}
                    disabled={isCompleted}
                    className="mt-0.5 text-slate-400 hover:text-teal-600 transition"
                  >
                    {isCompleted ? (
                      <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                    ) : (
                      <Square className="w-5 h-5" />
                    )}
                  </button>

                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-bold text-slate-900">
                        {task.beneficiary_id} - {task.beneficiary_name}
                      </span>
                      <span
                        className={`text-[10px] font-extrabold px-2 py-0.2 rounded-full uppercase ${
                          isEmergency
                            ? 'bg-red-100 text-red-800 border border-red-300'
                            : task.priority === 'HIGH'
                            ? 'bg-amber-100 text-amber-800'
                            : 'bg-slate-100 text-slate-700'
                        }`}
                      >
                        {task.priority}
                      </span>
                      <span className="text-[10px] bg-teal-50 text-teal-800 px-2 py-0.2 rounded font-semibold border border-teal-100">
                        {task.task_type}
                      </span>
                    </div>

                    <p className={`text-xs mt-1 font-medium ${isCompleted ? 'line-through text-slate-400' : 'text-slate-800'}`}>
                      {task.title}
                    </p>

                    {task.description && (
                      <p className="text-[11px] text-slate-500 mt-0.5">
                        {task.description}
                      </p>
                    )}
                  </div>
                </div>

                <div className="text-right shrink-0">
                  <span className="text-xs font-semibold text-slate-600 block">
                    {task.due_date}
                  </span>
                  <span
                    className={`text-[10px] font-bold uppercase mt-1 inline-block ${
                      isCompleted ? 'text-emerald-600' : 'text-amber-600'
                    }`}
                  >
                    {task.status}
                  </span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
