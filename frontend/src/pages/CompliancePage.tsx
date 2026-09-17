import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ShieldAlert,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Send,
  UserCheck,
  ArrowRight,
  RefreshCw,
  FileCheck
} from 'lucide-react';
import { checkCompliance, approveCampaign, sendForReview } from '../services/api';
import { CampaignContent, ComplianceResult } from '../types';
import { PageHeader } from '../components/common/PageHeader';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';

export const CompliancePage: React.FC = () => {
  const navigate = useNavigate();
  const [campaign, setCampaign] = useState<CampaignContent | null>(null);
  const [campaignId, setCampaignId] = useState<number | null>(null);
  const [consentConfirmed, setConsentConfirmed] = useState(false);
  const [complianceResult, setComplianceResult] = useState<ComplianceResult | null>(null);
  const [checking, setChecking] = useState(false);
  const [statusMessage, setStatusMessage] = useState<{ type: 'success' | 'error' | 'info'; text: string } | null>(null);
  const [isApproved, setIsApproved] = useState(false);

  useEffect(() => {
    const storedCampaign = localStorage.getItem('bankwise_active_campaign');
    const storedId = localStorage.getItem('bankwise_active_campaign_id');
    if (storedCampaign) {
      try {
        const parsed = JSON.parse(storedCampaign);
        setCampaign(parsed);
        if (storedId) setCampaignId(Number(storedId));
      } catch (e) {
        console.error(e);
      }
    }
  }, []);

  const runCheck = async () => {
    if (!campaign) return;
    try {
      setChecking(true);
      const res = await checkCompliance(campaign, consentConfirmed);
      setComplianceResult(res);
    } catch (err: any) {
      setStatusMessage({ type: 'error', text: 'Compliance check failed' });
    } finally {
      setChecking(false);
    }
  };

  useEffect(() => {
    if (campaign) {
      runCheck();
    }
  }, [campaign, consentConfirmed]);

  const handleSendForReview = async () => {
    if (!campaignId) return;
    try {
      await sendForReview(campaignId, 'Sent for human compliance review.');
      setStatusMessage({ type: 'info', text: 'Campaign submitted for manual compliance review.' });
    } catch (err: any) {
      setStatusMessage({ type: 'error', text: 'Failed to submit for review.' });
    }
  };

  const handleApprove = async () => {
    if (!campaignId) return;
    try {
      await approveCampaign(campaignId, complianceResult?.score, 'Human-in-the-loop approval granted by Marketing Lead');
      setIsApproved(true);
      setStatusMessage({ type: 'success', text: 'Campaign approved successfully! You can now proceed to Campaign Delivery.' });
      localStorage.setItem('bankwise_campaign_approved', 'true');
    } catch (err: any) {
      setStatusMessage({ type: 'error', text: 'Approval failed.' });
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Compliance & Human Approval"
        subtitle="Automated regulatory checks, flagged financial claims detection, and governance sign-off."
      />

      {statusMessage && (
        <div
          className={`p-4 rounded-xl text-xs font-semibold flex items-center justify-between ${
            statusMessage.type === 'success'
              ? 'bg-green-50 text-green-800 border border-green-200'
              : statusMessage.type === 'error'
              ? 'bg-red-50 text-red-800 border border-red-200'
              : 'bg-blue-50 text-blue-800 border border-blue-200'
          }`}
        >
          <span>{statusMessage.text}</span>
          <button onClick={() => setStatusMessage(null)}>✕</button>
        </div>
      )}

      {!campaign ? (
        <EmptyState
          title="No active campaign to check"
          description="Generate a campaign in Campaign Studio first to run automated compliance checks."
          action={
            <button
              onClick={() => navigate('/campaign-studio')}
              className="bg-[#00A896] text-white px-4 py-2 rounded-lg text-xs font-semibold hover:bg-[#008f80] transition-colors"
            >
              Go to Campaign Studio
            </button>
          }
        />
      ) : (
        <div className="space-y-6">
          {/* Campaign Context Header */}
          <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-xs flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 rounded-lg bg-[#1A3A5C] text-white flex items-center justify-center font-mono font-bold text-xs">
                #{campaignId || '1'}
              </div>
              <div>
                <h4 className="text-sm font-bold text-gray-900">{campaign.subject || campaign.subject_line || 'Marketing Campaign'}</h4>
                <div className="flex items-center space-x-3 text-xs text-gray-500 mt-0.5">
                  <span>Customer: <strong className="font-mono text-gray-700">{campaign.customer_id}</strong></span>
                  <span>Product: <strong className="text-gray-700">{campaign.product_name}</strong></span>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              {complianceResult && (
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-gray-500 font-semibold">Compliance Score:</span>
                  <span className="text-lg font-black text-[#1A3A5C]">{complianceResult.score}/100</span>
                </div>
              )}
            </div>
          </div>

          {/* Compliance Results Card */}
          <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-xs space-y-6">
            <div className="border-b border-gray-100 pb-4 flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-[#0A1628] flex items-center space-x-2">
                  <ShieldCheck className="w-4 h-4 text-[#00A896]" />
                  <span>Automated Regulatory Safety Checks</span>
                </h3>
                <p className="text-xs text-gray-500 mt-1">
                  Evaluates copy against prohibited financial phrases (e.g. "guaranteed returns", "risk-free", "instant loan approval").
                </p>
              </div>

              {complianceResult && (
                <Badge
                  variant={
                    complianceResult.status === 'Approved'
                      ? 'success'
                      : complianceResult.status === 'Needs Review'
                      ? 'warning'
                      : 'danger'
                  }
                >
                  {complianceResult.status}
                </Badge>
              )}
            </div>

            {/* Checklist of issues */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500">Validation Checks</h4>
              {complianceResult?.issues && complianceResult.issues.length > 0 ? (
                <div className="space-y-2">
                  {complianceResult.issues.map((issue, idx) => (
                    <div
                      key={idx}
                      className="p-3 bg-amber-50/80 border border-amber-200 rounded-lg text-xs text-amber-800 flex items-start space-x-2"
                    >
                      <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                      <span>{issue}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg text-xs text-green-800 flex items-center space-x-2">
                  <CheckCircle2 className="w-4 h-4 text-green-600" />
                  <span>All automated regulatory validations passed. No prohibited marketing phrases detected.</span>
                </div>
              )}
            </div>

            {/* Consent Confirmation Checkbox */}
            <div className="bg-[#F8FAFC] p-4 rounded-xl border border-gray-200">
              <label className="flex items-start space-x-3 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={consentConfirmed}
                  onChange={(e) => setConsentConfirmed(e.target.checked)}
                  className="mt-0.5 h-4 w-4 rounded border-gray-300 text-[#00A896] focus:ring-[#00A896]"
                />
                <div className="text-xs">
                  <span className="font-bold text-gray-800 block">
                    Channel Consent & Opt-In Verification
                  </span>
                  <span className="text-gray-500">
                    I confirm that the customer has a valid opt-in consent recorded for the selected outreach channel in compliance with DPDP & RBI guidelines.
                  </span>
                </div>
              </label>
            </div>

            {/* Human Approval Action Bar */}
            <div className="pt-4 border-t border-gray-100 flex flex-col sm:flex-row items-center justify-between gap-3">
              <button
                onClick={handleSendForReview}
                className="w-full sm:w-auto px-4 py-2.5 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 text-xs font-semibold transition-colors"
              >
                Send for Secondary Review
              </button>

              <div className="flex items-center space-x-3 w-full sm:w-auto">
                <button
                  onClick={handleApprove}
                  disabled={!consentConfirmed || Boolean(complianceResult && complianceResult.score < 50)}
                  className="w-full sm:w-auto px-6 py-2.5 bg-[#2E7D32] hover:bg-[#256629] text-white font-bold text-xs rounded-lg shadow-xs transition-colors flex items-center justify-center space-x-2 disabled:opacity-40"
                >
                  <UserCheck className="w-4 h-4" />
                  <span>Approve Campaign</span>
                </button>

                {isApproved && (
                  <button
                    onClick={() => navigate('/delivery')}
                    className="w-full sm:w-auto px-5 py-2.5 bg-[#00A896] hover:bg-[#008f80] text-white font-bold text-xs rounded-lg shadow-xs transition-colors flex items-center justify-center space-x-2"
                  >
                    <span>Proceed to Delivery</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
