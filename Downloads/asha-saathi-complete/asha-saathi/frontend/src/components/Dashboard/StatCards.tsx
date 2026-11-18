import React from 'react';
import { 
  Users, 
  Heart, 
  Baby, 
  Syringe, 
  AlertOctagon, 
  Clock 
} from 'lucide-react';

interface StatCardsProps {
  stats: {
    total_visits: number;
    pregnancy_visits: number;
    newborn_visits: number;
    immunisation_visits: number;
    urgent_referrals: number;
    pending_follow_ups: number;
    overdue_follow_ups: number;
    high_risk_beneficiaries: number;
  };
  onFilterType?: (type: string) => void;
}

export const StatCards: React.FC<StatCardsProps> = ({ stats, onFilterType }) => {
  const cards = [
    {
      title: 'Total Visits Recorded',
      count: stats.total_visits,
      icon: Users,
      color: 'text-teal-600',
      bg: 'bg-teal-50',
      border: 'border-teal-200',
      sub: 'All field registers',
      type: 'ALL',
    },
    {
      title: 'Pregnancy Visits (ANC)',
      count: stats.pregnancy_visits,
      icon: Heart,
      color: 'text-rose-600',
      bg: 'bg-rose-50',
      border: 'border-rose-200',
      sub: `${stats.high_risk_beneficiaries} high-risk mothers`,
      type: 'ANC',
    },
    {
      title: 'Newborn Visits (HBNC)',
      count: stats.newborn_visits,
      icon: Baby,
      color: 'text-blue-600',
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      sub: 'Postnatal care visits',
      type: 'NEWBORN',
    },
    {
      title: 'Immunisation Visits',
      count: stats.immunisation_visits,
      icon: Syringe,
      color: 'text-emerald-600',
      bg: 'bg-emerald-50',
      border: 'border-emerald-200',
      sub: 'National schedule',
      type: 'IMMUNISATION',
    },
    {
      title: 'Urgent Danger Referrals',
      count: stats.urgent_referrals,
      icon: AlertOctagon,
      color: 'text-red-600',
      bg: 'bg-red-50',
      border: 'border-red-300',
      sub: 'PHC / FRU escalated',
      alert: true,
      type: 'EMERGENCY',
    },
    {
      title: 'Overdue Follow-ups',
      count: stats.overdue_follow_ups,
      icon: Clock,
      color: 'text-amber-600',
      bg: 'bg-amber-50',
      border: 'border-amber-200',
      sub: `${stats.pending_follow_ups} pending in total`,
      type: 'PENDING',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 my-4">
      {cards.map((c, i) => {
        const Icon = c.icon;
        return (
          <div
            key={i}
            onClick={() => onFilterType?.(c.type)}
            className={`p-3.5 rounded-2xl bg-white border ${c.border} shadow-sm hover:shadow-md cursor-pointer transition-all duration-200 flex flex-col justify-between ${
              c.alert ? 'ring-2 ring-red-400' : ''
            }`}
          >
            <div className="flex items-center justify-between">
              <span className={`p-2 rounded-xl ${c.bg} ${c.color}`}>
                <Icon className="w-5 h-5 stroke-[2.2]" />
              </span>
              <span className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight">
                {c.count}
              </span>
            </div>
            <div className="mt-2.5">
              <h4 className="text-xs font-bold text-slate-700 leading-snug">{c.title}</h4>
              <p className="text-[11px] text-slate-400 font-medium mt-0.5">{c.sub}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
};
