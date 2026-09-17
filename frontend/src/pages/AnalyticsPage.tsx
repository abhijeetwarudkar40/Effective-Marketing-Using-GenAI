import React, { useEffect, useState } from 'react';
import { BarChart3, Send, CheckCircle2, RefreshCw, PieChart as PieIcon, ShieldCheck } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { getAnalyticsSummary, getCampaigns, getDeliveries } from '../services/api';
import { AnalyticsSummary, CampaignContent, DeliveryLog } from '../types';
import { PageHeader } from '../components/common/PageHeader';
import { KPICard } from '../components/common/KPICard';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export const AnalyticsPage: React.FC = () => {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [campaigns, setCampaigns] = useState<CampaignContent[]>([]);
  const [deliveries, setDeliveries] = useState<DeliveryLog[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      setLoading(true);
      const [sData, cData, dData] = await Promise.all([
        getAnalyticsSummary(),
        getCampaigns(),
        getDeliveries(),
      ]);
      setSummary(sData);
      setCampaigns(cData);
      setDeliveries(dData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) return <LoadingSpinner message="Aggregating performance analytics from SQLite..." />;

  // Prepare chart data
  const statusData = summary?.campaign_status_distribution
    ? Object.entries(summary.campaign_status_distribution).map(([status, count]) => ({
        status,
        count,
      }))
    : [];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Analytics & Delivery Performance"
        subtitle="Real-time execution analytics, approval status telemetry, and multi-channel delivery audit logs."
        actions={
          <button
            onClick={loadData}
            className="flex items-center space-x-1.5 px-3 py-2 bg-white border border-gray-300 rounded-lg text-xs font-semibold text-gray-700 hover:bg-gray-50 shadow-xs transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh Analytics</span>
          </button>
        }
      />

      {/* KPI Cards */}
      {summary && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard
            title="Total Campaigns In DB"
            value={summary.total_campaigns}
            subtitle="Generated & Saved Records"
            icon={BarChart3}
            accentColor="#1A3A5C"
          />
          <KPICard
            title="Human Approved"
            value={summary.approved_campaigns}
            subtitle="Cleared Compliance Sign-off"
            icon={CheckCircle2}
            accentColor="#2E7D32"
          />
          <KPICard
            title="Messages Dispatched"
            value={summary.messages_sent}
            subtitle="Email & SMS transmissions"
            icon={Send}
            accentColor="#00A896"
          />
          <KPICard
            title="Delivery Audit Logs"
            value={summary.delivery_records}
            subtitle="Recorded execution events"
            icon={ShieldCheck}
            accentColor="#C9A84C"
          />
        </div>
      )}

      {/* Analytics Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Campaign Status Breakdown */}
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-xs">
          <h3 className="text-sm font-bold text-[#0A1628] mb-4">Campaign Lifecycle Distribution</h3>
          {statusData.length === 0 ? (
            <div className="p-8 text-center text-xs text-gray-400">No lifecycle data recorded yet.</div>
          ) : (
            <div className="h-56 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={statusData} margin={{ top: 10, right: 10, left: -20, bottom: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#EDF2F7" />
                  <XAxis dataKey="status" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip contentStyle={{ borderRadius: '8px', fontSize: '12px' }} />
                  <Bar dataKey="count" fill="#1A3A5C" radius={[4, 4, 0, 0]} name="Campaigns" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* Customer Segment Breakdown */}
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-xs">
          <h3 className="text-sm font-bold text-[#0A1628] mb-4">Customer Segments Distribution</h3>
          {summary?.segment_distribution && summary.segment_distribution.length > 0 ? (
            <div className="h-56 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={summary.segment_distribution} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#EDF2F7" />
                  <XAxis dataKey="segment" angle={-20} textAnchor="end" interval={0} tick={{ fontSize: 9 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip contentStyle={{ borderRadius: '8px', fontSize: '12px' }} />
                  <Bar dataKey="count" fill="#00A896" radius={[4, 4, 0, 0]} name="Customers" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="p-8 text-center text-xs text-gray-400">No segment data available.</div>
          )}
        </div>
      </div>

      {/* Campaigns Table */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-xs overflow-hidden">
        <div className="p-4 border-b border-gray-100 flex items-center justify-between">
          <h3 className="text-sm font-bold text-[#0A1628]">Recent Campaigns (SQLite Database)</h3>
          <Badge variant="teal">{campaigns.length} Total</Badge>
        </div>

        <div className="overflow-x-auto max-h-80">
          <table className="w-full text-left border-collapse text-xs">
            <thead className="sticky top-0 bg-[#0A1628] text-white">
              <tr>
                <th className="py-2.5 px-4">ID</th>
                <th className="py-2.5 px-4">Customer</th>
                <th className="py-2.5 px-4">Product</th>
                <th className="py-2.5 px-4">Subject</th>
                <th className="py-2.5 px-4">Status</th>
                <th className="py-2.5 px-4">Score</th>
                <th className="py-2.5 px-4">Created</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {campaigns.map((c) => (
                <tr key={c.id || c.campaign_id} className="hover:bg-gray-50/80">
                  <td className="py-2.5 px-4 font-mono font-semibold text-[#1A3A5C]">#{c.id || c.campaign_id}</td>
                  <td className="py-2.5 px-4 font-mono text-gray-600">{c.customer_id}</td>
                  <td className="py-2.5 px-4 font-medium text-gray-900">{c.product_name}</td>
                  <td className="py-2.5 px-4 text-gray-600 max-w-xs truncate">{c.subject || c.subject_line}</td>
                  <td className="py-2.5 px-4">
                    <Badge variant={c.status === 'Approved' ? 'success' : c.status === 'Needs Review' ? 'warning' : 'neutral'}>
                      {c.status || 'Draft'}
                    </Badge>
                  </td>
                  <td className="py-2.5 px-4 font-mono font-semibold">{c.compliance_score ? `${c.compliance_score}/100` : '—'}</td>
                  <td className="py-2.5 px-4 text-gray-400 font-mono text-[11px]">
                    {c.created_at ? new Date(c.created_at).toLocaleDateString() : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
