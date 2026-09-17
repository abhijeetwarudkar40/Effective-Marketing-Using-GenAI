import React, { useEffect, useState } from 'react';
import { ShieldCheck, Lock, UserCheck, FileText, CheckCircle2, AlertTriangle, EyeOff } from 'lucide-react';
import { PageHeader } from '../components/common/PageHeader';
import { Badge } from '../components/common/Badge';
import { getDeliveries, getCampaigns } from '../services/api';

export const GovernancePage: React.FC = () => {
  const [deliveries, setDeliveries] = useState<any[]>([]);
  const [campaigns, setCampaigns] = useState<any[]>([]);

  useEffect(() => {
    const load = async () => {
      try {
        const [d, c] = await Promise.all([getDeliveries(), getCampaigns()]);
        setDeliveries(d);
        setCampaigns(c);
      } catch (err) {
        console.error(err);
      }
    };
    load();
  }, []);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Governance, Risk & Responsible AI"
        subtitle="End-to-end regulatory compliance, human-in-the-loop sign-off audits, and customer data privacy enforcement."
      />

      {/* Governance Architecture Diagram Card */}
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-xs">
        <h3 className="text-sm font-bold text-[#0A1628] mb-2 flex items-center space-x-2">
          <ShieldCheck className="w-4 h-4 text-[#00A896]" />
          <span>BankWise AI Responsible Campaign Lifecycle</span>
        </h3>
        <p className="text-xs text-gray-500 mb-6">
          Strict gated pipeline preventing unapproved AI content from reaching banking customers.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl bg-gray-50 border border-gray-200 text-center relative flex flex-col justify-between">
            <div>
              <div className="w-8 h-8 rounded-full bg-[#1A3A5C] text-white flex items-center justify-center mx-auto mb-2 text-xs font-bold">1</div>
              <h4 className="text-xs font-bold text-[#0A1628]">GenAI Generation</h4>
              <p className="text-[11px] text-gray-500 mt-1">Contextual copy created via Gemini 3.6 Flash without exposing PII</p>
            </div>
            <span className="text-[10px] text-[#00A896] font-bold mt-2">DRAFT STATE</span>
          </div>

          <div className="p-4 rounded-xl bg-gray-50 border border-gray-200 text-center relative flex flex-col justify-between">
            <div>
              <div className="w-8 h-8 rounded-full bg-[#00A896] text-white flex items-center justify-center mx-auto mb-2 text-xs font-bold">2</div>
              <h4 className="text-xs font-bold text-[#0A1628]">Safety Validation</h4>
              <p className="text-[11px] text-gray-500 mt-1">Algorithmic scan for prohibited financial guarantees & claims</p>
            </div>
            <span className="text-[10px] text-[#00A896] font-bold mt-2">COMPLIANCE CHECK</span>
          </div>

          <div className="p-4 rounded-xl bg-gray-50 border border-gray-200 text-center relative flex flex-col justify-between">
            <div>
              <div className="w-8 h-8 rounded-full bg-[#C9A84C] text-white flex items-center justify-center mx-auto mb-2 text-xs font-bold">3</div>
              <h4 className="text-xs font-bold text-[#0A1628]">Human-in-the-Loop</h4>
              <p className="text-[11px] text-gray-500 mt-1">Marketing Lead consent verification and manual approval</p>
            </div>
            <span className="text-[10px] text-[#C9A84C] font-bold mt-2">MANDATORY SIGN-OFF</span>
          </div>

          <div className="p-4 rounded-xl bg-gray-50 border border-gray-200 text-center relative flex flex-col justify-between">
            <div>
              <div className="w-8 h-8 rounded-full bg-[#2E7D32] text-white flex items-center justify-center mx-auto mb-2 text-xs font-bold">4</div>
              <h4 className="text-xs font-bold text-[#0A1628]">Secure Dispatch</h4>
              <p className="text-[11px] text-gray-500 mt-1">TLS-encrypted email/SMS dispatch with permanent SQLite audit log</p>
            </div>
            <span className="text-[10px] text-[#2E7D32] font-bold mt-2">AUDITED DELIVERY</span>
          </div>
        </div>
      </div>

      {/* Safety & Compliance Controls Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-xs space-y-3">
          <div className="w-10 h-10 rounded-lg bg-[#1A3A5C]/10 text-[#1A3A5C] flex items-center justify-center">
            <EyeOff className="w-5 h-5" />
          </div>
          <h4 className="text-sm font-bold text-gray-900">Zero PII Prompting</h4>
          <p className="text-xs text-gray-600 leading-relaxed">
            Customer identifiers, account balances, and phone numbers are stripped before prompt formulation. Only anonymized behavioral traits and recommendation angles are processed by Gemini.
          </p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-xs space-y-3">
          <div className="w-10 h-10 rounded-lg bg-[#00A896]/10 text-[#00A896] flex items-center justify-center">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <h4 className="text-sm font-bold text-gray-900">Regulatory Keyword Guardrails</h4>
          <p className="text-xs text-gray-600 leading-relaxed">
            Deterministic token filtering detects deceptive promises (e.g. "100% guaranteed approval", "zero risk", "guaranteed profit") and flags campaigns for rejection.
          </p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-xs space-y-3">
          <div className="w-10 h-10 rounded-lg bg-[#C9A84C]/10 text-[#C9A84C] flex items-center justify-center">
            <Lock className="w-5 h-5" />
          </div>
          <h4 className="text-sm font-bold text-gray-900">Secret Isolation</h4>
          <p className="text-xs text-gray-600 leading-relaxed">
            API keys, Gmail SMTP credentials, and SQLite database connection strings reside strictly in backend environment variables, inaccessible from browser clients.
          </p>
        </div>
      </div>

      {/* Audit Logs Summary */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-xs p-6 space-y-4">
        <div className="flex items-center justify-between border-b border-gray-100 pb-3">
          <div>
            <h3 className="text-sm font-bold text-[#0A1628]">Immutable Compliance Audit Trail</h3>
            <p className="text-xs text-gray-500">Recorded approval and transmission timestamps</p>
          </div>
          <Badge variant="teal">{deliveries.length} Recorded Events</Badge>
        </div>

        <div className="space-y-2">
          {deliveries.slice(0, 5).map((d) => (
            <div key={d.id} className="p-3 bg-gray-50 rounded-lg text-xs flex items-center justify-between border border-gray-100">
              <div className="flex items-center space-x-3">
                <span className="font-mono text-gray-500">#{d.id}</span>
                <span className="font-semibold text-gray-800">Campaign #{d.campaign_id}</span>
                <span className="text-gray-500">via {d.channel} to <strong className="font-mono">{d.recipient}</strong></span>
              </div>
              <div className="flex items-center space-x-3">
                <Badge variant={d.status === 'SENT' || d.status === 'DRY_RUN_SIMULATED' ? 'success' : 'danger'}>
                  {d.status}
                </Badge>
                <span className="text-gray-400 font-mono text-[11px]">
                  {new Date(d.created_at).toLocaleString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
