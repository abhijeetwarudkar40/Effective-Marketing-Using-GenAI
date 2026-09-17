import React, { useEffect, useState } from 'react';
import { Award, GitCompare, CheckCircle2, TrendingUp, HelpCircle, Layers } from 'lucide-react';
import { getABTestingAnalytics, getABTestingVariants } from '../services/api';
import { ABAnalytics } from '../types';
import { PageHeader } from '../components/common/PageHeader';
import { KPICard } from '../components/common/KPICard';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export const ABTestingPage: React.FC = () => {
  const [analytics, setAnalytics] = useState<ABAnalytics | null>(null);
  const [variants, setVariants] = useState<any[]>([]);
  const [totalVariants, setTotalVariants] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  // Active session variants
  const [activeVariantA, setActiveVariantA] = useState<any | null>(null);
  const [activeVariantB, setActiveVariantB] = useState<any | null>(null);

  useEffect(() => {
    const va = localStorage.getItem('bankwise_active_variant_a');
    const vb = localStorage.getItem('bankwise_active_variant_b');
    if (va) setActiveVariantA(JSON.parse(va));
    if (vb) setActiveVariantB(JSON.parse(vb));

    const loadData = async () => {
      try {
        setLoading(true);
        const [anData, vData] = await Promise.all([
          getABTestingAnalytics(),
          getABTestingVariants(page, 10),
        ]);
        setAnalytics(anData);
        setVariants(vData.variants);
        setTotalVariants(vData.total);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [page]);

  if (loading) return <LoadingSpinner message="Calculating A/B model evaluation scores..." />;

  return (
    <div className="space-y-6">
      <PageHeader
        title="A/B Strategy Testing & Evaluation"
        subtitle="Multi-variant evaluation comparing Benefit-Focused (Variant A) vs. Action-Focused (Variant B) copywriting."
      />

      {/* KPI Cards */}
      {analytics && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard
            title="Winning Strategy"
            value={analytics.top_strategy}
            subtitle="Overall model preference"
            icon={Award}
            accentColor="#00A896"
          />
          <KPICard
            title="Variant A Wins"
            value={`${analytics.a_wins} (${analytics.total ? ((analytics.a_wins / analytics.total) * 100).toFixed(1) : 0}%)`}
            subtitle="Benefit-Focused approach"
            accentColor="#1A3A5C"
          />
          <KPICard
            title="Variant B Wins"
            value={`${analytics.b_wins} (${analytics.total ? ((analytics.b_wins / analytics.total) * 100).toFixed(1) : 0}%)`}
            subtitle="Action-Focused approach"
            accentColor="#2C5F8A"
          />
          <KPICard
            title="Average Score Gap"
            value={`${analytics.score_gap} pts`}
            subtitle="Diff between variants"
            accentColor="#C9A84C"
          />
        </div>
      )}

      {/* Active Campaign Live Side-by-Side Comparison */}
      {activeVariantA && activeVariantB && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-xs p-6 space-y-4">
          <div className="flex items-center justify-between border-b border-gray-100 pb-3">
            <div>
              <h3 className="text-sm font-bold text-[#0A1628] flex items-center space-x-2">
                <GitCompare className="w-4 h-4 text-[#00A896]" />
                <span>Active Campaign Live A/B Comparison</span>
              </h3>
              <p className="text-xs text-gray-500">Gemini generated copy for the currently active customer campaign</p>
            </div>
            <Badge variant="teal">Live Active Pair</Badge>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Variant A Card */}
            <div className="p-5 rounded-xl border border-[#1A3A5C]/30 bg-[#F8FAFC] space-y-3 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-[#1A3A5C] bg-[#1A3A5C]/10 px-2.5 py-0.5 rounded-md">
                    Variant A · Benefit-Focused
                  </span>
                  <span className="text-xs font-bold text-gray-700">Value Emphasis</span>
                </div>

                <div className="mt-3 space-y-2 text-xs">
                  <div>
                    <span className="font-bold text-gray-500 block text-[10px] uppercase">Subject</span>
                    <p className="font-bold text-[#0056B3]">{activeVariantA.subject || activeVariantA.subject_line}</p>
                  </div>
                  {activeVariantA.headline && (
                    <div>
                      <span className="font-bold text-gray-500 block text-[10px] uppercase">Headline</span>
                      <p className="font-semibold text-gray-900">{activeVariantA.headline}</p>
                    </div>
                  )}
                  <div>
                    <span className="font-bold text-gray-500 block text-[10px] uppercase">Body</span>
                    <p className="text-gray-700 leading-relaxed whitespace-pre-line">{activeVariantA.email_body || activeVariantA.body}</p>
                  </div>
                  {activeVariantA.cta && (
                    <div>
                      <span className="font-bold text-gray-500 block text-[10px] uppercase">CTA</span>
                      <span className="inline-block px-3 py-1 bg-[#1A3A5C] text-white font-semibold text-[11px] rounded">
                        {activeVariantA.cta}
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {activeVariantA.variant_rationale && (
                <div className="mt-3 pt-3 border-t border-gray-200 text-[11px] text-gray-500 italic">
                  <strong>Rationale:</strong> {activeVariantA.variant_rationale}
                </div>
              )}
            </div>

            {/* Variant B Card */}
            <div className="p-5 rounded-xl border border-[#00A896]/40 bg-[#F0FDF4] space-y-3 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-[#007A6C] bg-[#00A896]/15 px-2.5 py-0.5 rounded-md">
                    Variant B · Action-Focused
                  </span>
                  <span className="text-xs font-bold text-gray-700">Direct Next-Step</span>
                </div>

                <div className="mt-3 space-y-2 text-xs">
                  <div>
                    <span className="font-bold text-gray-500 block text-[10px] uppercase">Subject</span>
                    <p className="font-bold text-[#0056B3]">{activeVariantB.subject || activeVariantB.subject_line}</p>
                  </div>
                  {activeVariantB.headline && (
                    <div>
                      <span className="font-bold text-gray-500 block text-[10px] uppercase">Headline</span>
                      <p className="font-semibold text-gray-900">{activeVariantB.headline}</p>
                    </div>
                  )}
                  <div>
                    <span className="font-bold text-gray-500 block text-[10px] uppercase">Body</span>
                    <p className="text-gray-700 leading-relaxed whitespace-pre-line">{activeVariantB.email_body || activeVariantB.body}</p>
                  </div>
                  {activeVariantB.cta && (
                    <div>
                      <span className="font-bold text-gray-500 block text-[10px] uppercase">CTA</span>
                      <span className="inline-block px-3 py-1 bg-[#00A896] text-white font-semibold text-[11px] rounded">
                        {activeVariantB.cta}
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {activeVariantB.variant_rationale && (
                <div className="mt-3 pt-3 border-t border-green-200 text-[11px] text-gray-500 italic">
                  <strong>Rationale:</strong> {activeVariantB.variant_rationale}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Dataset A/B Testing Evaluation Table */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-xs overflow-hidden">
        <div className="p-4 border-b border-gray-100 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-[#0A1628]">Pre-Generated A/B Variant Pool</h3>
            <p className="text-xs text-gray-500">Variants from campaign_ab_variants.csv evaluated across customers</p>
          </div>
          <Badge variant="neutral">{totalVariants} Pairs</Badge>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-[#0A1628] text-gray-200 border-b border-[#1A3A5C]">
                <th className="py-3 px-4 font-semibold uppercase tracking-wider">Customer ID</th>
                <th className="py-3 px-4 font-semibold uppercase tracking-wider">Product</th>
                <th className="py-3 px-4 font-semibold uppercase tracking-wider">Variant A Subject</th>
                <th className="py-3 px-4 font-semibold uppercase tracking-wider">Variant B Subject</th>
                <th className="py-3 px-4 font-semibold uppercase tracking-wider">Strategy</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {variants.map((v, i) => (
                <tr key={i} className="hover:bg-gray-50/80">
                  <td className="py-3 px-4 font-mono font-semibold text-[#1A3A5C]">{v.customer_id}</td>
                  <td className="py-3 px-4 font-medium text-gray-900">{v.product_name}</td>
                  <td className="py-3 px-4 text-gray-600 max-w-xs truncate">{v.variant_a_subject || v.variant_a_subject_line || '—'}</td>
                  <td className="py-3 px-4 text-gray-600 max-w-xs truncate">{v.variant_b_subject || v.variant_b_subject_line || '—'}</td>
                  <td className="py-3 px-4">
                    <Badge variant="teal">{v.winning_strategy || 'Action-Focused'}</Badge>
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
