import React, { useEffect, useState } from 'react';
import { PieChart as PieIcon, Users, TrendingUp, AlertTriangle, Target } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { getSegments } from '../services/api';
import { SegmentsResponse } from '../types';
import { PageHeader } from '../components/common/PageHeader';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { KPICard } from '../components/common/KPICard';
import { Badge } from '../components/common/Badge';

export const SegmentsPage: React.FC = () => {
  const [data, setData] = useState<SegmentsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const res = await getSegments();
        setData(res);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) return <LoadingSpinner message="Calculating segment distributions & profiling..." />;
  if (!data) return <div className="p-6 text-red-600 bg-red-50 rounded-xl">Failed to load segments.</div>;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Customer Segments & Behavioral Insights"
        subtitle="Unsupervised machine learning clustering profiles, customer personas, and retention risk distributions."
      />

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <KPICard
          title="Total Segmented Customers"
          value={data.total_customers.toLocaleString()}
          subtitle="Processed banking accounts"
          icon={Users}
          accentColor="#1A3A5C"
        />
        <KPICard
          title="Distinct Clusters"
          value={data.segments.length}
          subtitle="K-Means & RFM classification"
          icon={PieIcon}
          accentColor="#00A896"
        />
        <KPICard
          title="Unique Personas"
          value={data.persona_distribution.length}
          subtitle="Behavioral persona mappings"
          icon={Target}
          accentColor="#C9A84C"
        />
      </div>

      {/* Segment Cards Grid */}
      <div>
        <h3 className="text-sm font-bold text-[#0A1628] uppercase tracking-wider mb-4">Segment Profiles</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data.segments.map((seg, idx) => (
            <div
              key={seg.segment}
              className="bg-white rounded-xl p-5 border border-gray-200 shadow-xs hover:border-[#00A896]/50 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-[#00A896] bg-[#00A896]/10 px-2.5 py-0.5 rounded-full">
                    Cluster #{idx + 1}
                  </span>
                  <span className="text-xs font-semibold text-gray-500">{seg.percentage}% of total</span>
                </div>
                <h4 className="text-base font-bold text-[#0A1628] mt-2 tracking-tight">{seg.segment}</h4>
                <p className="text-2xl font-extrabold text-[#1A3A5C] mt-1">{seg.count.toLocaleString()} <span className="text-xs font-normal text-gray-500">customers</span></p>
              </div>

              <div className="mt-4 pt-3 border-t border-gray-100 space-y-2 text-xs">
                <div className="flex justify-between items-center">
                  <span className="text-gray-500">Top Persona:</span>
                  <span className="font-semibold text-gray-800">{seg.top_persona || 'Standard'}</span>
                </div>
                {seg.top_retention_risk && (
                  <div className="flex justify-between items-center">
                    <span className="text-gray-500">Retention Risk:</span>
                    <Badge variant={seg.top_retention_risk.toLowerCase().includes('high') ? 'danger' : 'success'}>
                      {seg.top_retention_risk}
                    </Badge>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Detailed Distribution Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Customer Personas */}
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold text-[#0A1628]">Customer Persona Distribution</h3>
            <Badge variant="teal">AI Classification</Badge>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.persona_distribution} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#EDF2F7" />
                <XAxis dataKey="persona" angle={-25} textAnchor="end" interval={0} tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={{ borderRadius: '8px', fontSize: '12px' }} />
                <Bar dataKey="count" fill="#2C5F8A" radius={[4, 4, 0, 0]} name="Customers" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Retention Risk & Priority */}
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold text-[#0A1628]">Retention Risk Assessment</h3>
            <Badge variant="warning">Churn Prevention</Badge>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.risk_distribution} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#EDF2F7" />
                <XAxis dataKey="risk" angle={-20} textAnchor="end" interval={0} tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={{ borderRadius: '8px', fontSize: '12px' }} />
                <Bar dataKey="count" fill="#C9A84C" radius={[4, 4, 0, 0]} name="Customers" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
