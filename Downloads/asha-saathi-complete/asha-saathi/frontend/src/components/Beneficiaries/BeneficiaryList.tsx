import React, { useState } from 'react';
import { Users, Search, Mic, Heart, Baby, ShieldAlert, Phone } from 'lucide-react';
import { Beneficiary } from '../../types/beneficiary';

interface BeneficiaryListProps {
  beneficiaries: Beneficiary[];
  onStartVoiceVisit: (ben: Beneficiary) => void;
}

export const BeneficiaryList: React.FC<BeneficiaryListProps> = ({
  beneficiaries,
  onStartVoiceVisit,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [villageFilter, setVillageFilter] = useState('ALL');

  const filtered = beneficiaries.filter((b) => {
    const matchesSearch =
      b.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      b.id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesVillage = villageFilter === 'ALL' || b.village === villageFilter;
    return matchesSearch && matchesVillage;
  });

  const villages = Array.from(new Set(beneficiaries.map((b) => b.village)));

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-4 sm:p-5 shadow-sm my-4">
      {/* Header and Search */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-100 gap-3">
        <div className="flex items-center space-x-2">
          <Users className="w-5 h-5 text-teal-600" />
          <h3 className="font-bold text-slate-900 text-sm sm:text-base">
            Catchment Register (Synthetic Beneficiaries)
          </h3>
        </div>

        <div className="flex items-center space-x-2">
          {/* Search Input */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search name or ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-8 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-teal-500 w-36 sm:w-48 text-slate-800"
            />
          </div>

          {/* Village Filter */}
          <select
            value={villageFilter}
            onChange={(e) => setVillageFilter(e.target.value)}
            className="py-1.5 px-2.5 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-700 focus:outline-none focus:ring-2 focus:ring-teal-500 font-medium"
          >
            <option value="ALL">All Villages</option>
            {villages.map((v) => (
              <option key={v} value={v}>
                {v}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Beneficiary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 mt-3">
        {filtered.map((b) => (
          <div
            key={b.id}
            className="p-3.5 rounded-xl border border-slate-200 hover:border-teal-300 transition-all bg-white shadow-sm hover:shadow flex flex-col justify-between"
          >
            <div>
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center space-x-1.5">
                    <span className="text-xs font-black text-slate-900 tracking-tight">
                      {b.name}
                    </span>
                    <span className="text-[10px] font-semibold text-slate-500">
                      ({b.id})
                    </span>
                  </div>
                  <span className="text-[11px] text-slate-500 font-medium block mt-0.5">
                    Village: {b.village} • Age: {b.age || 'N/A'}
                  </span>
                </div>

                <span
                  className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase ${
                    b.category === 'PREGNANT'
                      ? 'bg-rose-100 text-rose-800'
                      : b.category === 'NEWBORN'
                      ? 'bg-blue-100 text-blue-800'
                      : 'bg-emerald-100 text-emerald-800'
                  }`}
                >
                  {b.category}
                </span>
              </div>

              {/* Clinical Details */}
              <div className="mt-2 text-[11px] text-slate-600 space-y-0.5 bg-slate-50 p-2 rounded-lg">
                {b.category === 'PREGNANT' && b.edd_date && (
                  <p>
                    <span className="text-slate-400">EDD:</span>{' '}
                    <strong className="text-slate-800">{b.edd_date}</strong> (Gravida {b.parity || 1})
                  </p>
                )}
                {b.category === 'NEWBORN' && (
                  <p>
                    <span className="text-slate-400">DOB:</span>{' '}
                    <strong className="text-slate-800">{b.infant_dob}</strong> • Birth Wt:{' '}
                    <strong>{b.birth_weight_kg} kg</strong>
                  </p>
                )}
                {b.phone && (
                  <p className="flex items-center text-slate-500">
                    <Phone className="w-3 h-3 mr-1 text-slate-400" />
                    {b.phone}
                  </p>
                )}
              </div>

              {/* High Risk Flag */}
              {b.high_risk && (
                <div className="mt-2 px-2 py-1 bg-red-50 border border-red-200 rounded-md text-[11px] text-red-800 flex items-center space-x-1 font-semibold">
                  <ShieldAlert className="w-3 h-3 text-red-600 shrink-0" />
                  <span className="truncate">High-Risk: {b.high_risk_reason || 'Monitored Case'}</span>
                </div>
              )}
            </div>

            {/* Action: Voice Visit */}
            <div className="mt-3 pt-2 border-t border-slate-100 flex items-center justify-between">
              <span className="text-[11px] text-slate-400 font-medium">Synthetic Record</span>
              <button
                onClick={() => onStartVoiceVisit(b)}
                className="px-3 py-1.5 rounded-lg bg-teal-50 hover:bg-teal-100 text-teal-800 text-xs font-bold transition flex items-center space-x-1 border border-teal-200"
              >
                <Mic className="w-3 h-3 text-teal-600" />
                <span>Voice Visit</span>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
