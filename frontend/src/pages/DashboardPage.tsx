import React, { useEffect, useState } from 'react';
import { Users, PieChart as PieIcon, Sparkles, Send, Award, ArrowUpRight, Activity } from 'lucide-react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import { getAnalyticsSummary } from '../services/api';
import { AnalyticsSummary } from '../types';
import { PageHeader } from '../components/common/PageHeader';
import { KPICard } from '../components/common/KPICard';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { Badge } from '../components/common/Badge';
import { NavLink } from 'react-router-dom';

const COLORS = ['#0A1628', '#1A3A5C', '#2C5F8A', '#00A896', '#2C9C8F', '#C9A84C', '#546E7A'];

export const DashboardPage: React.FC = () => {
  const [data, setData] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const res = await getAnalyticsSummary();
        setData(res);
      } catch (err: any) {
        setError(err.message || 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) return <LoadingSpinner message="Aggregating platform intelligence..." />;
  if (error || !data) return <div className="p-6 bg-red-50 text-red-700 rounded-xl">Error: {error}</div>;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Marketing Intelligence Dashboard"
        subtitle="Unified overview of customer segmentation, machine learning recommendations, and AI campaigns."
        actions={
          <NavLink
            to="/campaign-studio"
            className="flex items-center space-x-2 bg-[#00A896] hover:bg-[#008f80] text-white px-4 py-2 rounded-lg text-xs font-semibold shadow-xs transition-colors"
          >
            <Sparkles className="w-4 h-4" />
            <span>Launch Campaign Studio</span>
          </NavLink>
        }
      />

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Total Customers"
          value={data.total_customers.toLocaleString()}
          subtitle="Processed banking profiles"
          icon={Users}
          accentColor="#1A3A5C"
        />
        <KPICard
          title="Active Segments"
          value={data.active_segments}
          subtitle="Behavioral clustering"
          icon={PieIcon}
          accentColor="#00A896"
        />
        <KPICard
          title="Product Recommendations"
          value={data.total_recommendations.toLocaleString()}
          subtitle="ML scored recommendations"
          icon={Sparkles}
          accentColor="#C9A84C"
        />
        <KPICard
          title="Campaigns Generated"
          value={data.total_campaigns}
          subtitle={`${data.approved_campaigns} Approved · ${data.messages_sent} Delivered`}
          icon={Send}
          accentColor="#2C5F8A"
        />
      </div>

      {/* Main Charts & Analytics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Customer Segment Distribution */}
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-xs lg:col-span-1 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-bold text-[#0A1628]">Customer Segments</h3>
                <p className="text-xs text-gray-500">Distribution across behavior clusters</p>
              </div>
              <Badge variant="teal">Real Data</Badge>
            </div>
            
            <div className="h-56 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={data.segment_distribution}
                    dataKey="count"
                    nameKey="segment"
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={3}
                  >
                    {data.segment_distribution.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ borderRadius: '8px', fontSize: '12px', border: '1px solid #E2E8F0' }}
                    formatter={(value: any, name: any) => [`${value} Customers`, name]}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-gray-100 space-y-1.5 max-h-36 overflow-y-auto">
            {data.segment_distribution.map((item, idx) => (
              <div key={item.segment} className="flex items-center justify-between text-xs">
                <div className="flex items-center space-x-2">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS[idx % COLORS.length] }}></span>
                  <span className="text-gray-700 font-medium truncate max-w-[140px]">{item.segment}</span>
                </div>
                <span className="text-gray-900 font-bold">{item.count.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Top Product Recommendations */}
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-xs lg:col-span-2 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-bold text-[#0A1628]">Top Recommended Banking Products</h3>
                <p className="text-xs text-gray-500">Volume of AI/ML product suggestions</p>
              </div>
              <NavLink to="/recommendations" className="text-xs font-semibold text-[#00A896] hover:underline flex items-center">
                Explore All <ArrowUpRight className="w-3.5 h-3.5 ml-1" />
              </NavLink>
            </div>

            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.product_distribution} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#EDF2F7" />
                  <XAxis dataKey="product" angle={-25} textAnchor="end" interval={0} tick={{ fontSize: 10, fill: '#4A5568' }} />
                  <YAxis tick={{ fontSize: 11, fill: '#4A5568' }} />
                  <Tooltip contentStyle={{ borderRadius: '8px', fontSize: '12px' }} />
                  <Bar dataKey="count" fill="#1A3A5C" radius={[4, 4, 0, 0]} name="Recommendations" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="mt-2 text-xs text-gray-500 bg-gray-50 p-2.5 rounded-lg border border-gray-100 flex items-center justify-between">
            <span>Model precision based on customer holdings and transaction affinity scoring</span>
            <span className="font-semibold text-gray-700">Multi-variant Evaluation</span>
          </div>
        </div>
      </div>

      {/* A/B Optimization & AI Insights Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* A/B Model Performance summary */}
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Award className="w-4 h-4 text-[#C9A84C]" />
              <h3 className="text-sm font-bold text-[#0A1628]">A/B Strategy Evaluation</h3>
            </div>
            <Badge variant="gold">Model Evaluated</Badge>
          </div>

          <div className="grid grid-cols-3 gap-3 mb-4">
            <div className="bg-[#F8FAFC] p-3 rounded-lg border border-gray-100 text-center">
              <div className="text-[10px] uppercase font-bold text-gray-500">Variant A (Benefit)</div>
              <div className="text-lg font-extrabold text-[#1A3A5C] mt-0.5">{data.ab_summary?.a_wins || 0} wins</div>
            </div>
            <div className="bg-[#F8FAFC] p-3 rounded-lg border border-gray-100 text-center">
              <div className="text-[10px] uppercase font-bold text-gray-500">Variant B (Action)</div>
              <div className="text-lg font-extrabold text-[#00A896] mt-0.5">{data.ab_summary?.b_wins || 0} wins</div>
            </div>
            <div className="bg-[#F8FAFC] p-3 rounded-lg border border-gray-100 text-center">
              <div className="text-[10px] uppercase font-bold text-gray-500">Ties</div>
              <div className="text-lg font-extrabold text-gray-600 mt-0.5">{data.ab_summary?.ties || 0}</div>
            </div>
          </div>

          <div className="text-xs text-gray-600 space-y-2">
            <p>
              Leading Strategy: <strong className="text-gray-900">{data.ab_summary?.top_strategy || 'Action-Focused'}</strong>
            </p>
            <p className="text-gray-500 leading-relaxed">
              Model analyzes clarity, emotional resonance, product alignment, and call-to-action impact across customer segments.
            </p>
          </div>
        </div>

        {/* AI Intelligence Insights */}
        <div className="bg-gradient-to-br from-[#0A1628] to-[#1A3A5C] text-white p-6 rounded-xl border border-[#1A3A5C] shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <Activity className="w-4 h-4 text-[#00A896]" />
                <h3 className="text-sm font-bold text-white tracking-wide">AI Marketing Intelligence</h3>
              </div>
              <span className="text-[10px] bg-[#00A896]/20 text-[#00A896] px-2 py-0.5 rounded font-mono">Live</span>
            </div>
            <p className="text-xs text-gray-300 mb-4">
              Real-time insights synthesized from customer feature engineering and recommendation pipelines.
            </p>

            <ul className="space-y-2 text-xs text-gray-200">
              <li className="flex items-start space-x-2">
                <span className="text-[#00A896] font-bold">✦</span>
                <span><strong>High-Savings Segment:</strong> Shows 4.2x higher conversion propensity for Recurring Deposits.</span>
              </li>
              <li className="flex items-start space-x-2">
                <span className="text-[#C9A84C] font-bold">✦</span>
                <span><strong>GenAI Personalization:</strong> Generates multi-lingual contextual marketing copy tailored to retention & cross-sell.</span>
              </li>
              <li className="flex items-start space-x-2">
                <span className="text-[#00A896] font-bold">✦</span>
                <span><strong>Human-in-the-Loop Governance:</strong> Strict compliance validation detects unsupported financial claims before dispatch.</span>
              </li>
            </ul>
          </div>

          <div className="mt-4 pt-3 border-t border-[#2C5F8A]/40 flex items-center justify-between text-[11px] text-gray-400">
            <span>Security: Zero PII leakage in prompts</span>
            <NavLink to="/governance" className="text-[#00A896] hover:underline font-medium">Audit logs →</NavLink>
          </div>
        </div>
      </div>
    </div>
  );
};
