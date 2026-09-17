import React, { useEffect, useState } from 'react';
import { Sparkles, Search, Filter, ChevronLeft, ChevronRight, CheckCircle2 } from 'lucide-react';
import { getRecommendations, getRecommendationProductsList, getRecommendationsSummary } from '../services/api';
import { Recommendation, RecommendationsSummary } from '../types';
import { PageHeader } from '../components/common/PageHeader';
import { KPICard } from '../components/common/KPICard';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';

export const RecommendationsPage: React.FC = () => {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [products, setProducts] = useState<string[]>([]);
  const [summary, setSummary] = useState<RecommendationsSummary | null>(null);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [pageSize] = useState(25);
  const [selectedProduct, setSelectedProduct] = useState('All');
  const [customerIdSearch, setCustomerIdSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadInitial = async () => {
      try {
        const [prods, sum] = await Promise.all([
          getRecommendationProductsList(),
          getRecommendationsSummary(),
        ]);
        setProducts(prods);
        setSummary(sum);
      } catch (err) {
        console.error(err);
      }
    };
    loadInitial();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const res = await getRecommendations(page, pageSize, customerIdSearch, selectedProduct);
      setRecommendations(res.recommendations);
      setTotal(res.total);
      setPages(res.pages);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [page, selectedProduct]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    loadData();
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Product Recommendations Engine"
        subtitle="Machine learning scored product recommendations with explainability reasons and objective mapping."
      />

      {/* KPI Overview */}
      {summary && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <KPICard
            title="Total Recommendations"
            value={summary.total.toLocaleString()}
            subtitle="Generated scored associations"
            icon={Sparkles}
            accentColor="#00A896"
          />
          <KPICard
            title="Unique Customers"
            value={summary.customers.toLocaleString()}
            subtitle="Eligible account holders"
            accentColor="#1A3A5C"
          />
          <KPICard
            title="Product Catalog"
            value={summary.products}
            subtitle="Active banking products"
            accentColor="#C9A84C"
          />
        </div>
      )}

      {/* Filters and Search */}
      <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <form onSubmit={handleSearch} className="flex-1 flex items-center space-x-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by Customer ID..."
              value={customerIdSearch}
              onChange={(e) => setCustomerIdSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 text-xs border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#00A896]/20 focus:border-[#00A896]"
            />
          </div>
          <button
            type="submit"
            className="bg-[#1A3A5C] text-white px-4 py-2 rounded-lg text-xs font-semibold hover:bg-[#0A1628] transition-colors"
          >
            Filter Customer
          </button>
        </form>

        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-500" />
            <span className="text-xs font-semibold text-gray-700">Product:</span>
          </div>
          <select
            value={selectedProduct}
            onChange={(e) => {
              setSelectedProduct(e.target.value);
              setPage(1);
            }}
            className="text-xs border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#00A896]/20 focus:border-[#00A896]"
          >
            <option value="All">All Products</option>
            {products.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Recommendations Table */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-xs overflow-hidden">
        {loading ? (
          <LoadingSpinner message="Loading recommendations..." />
        ) : recommendations.length === 0 ? (
          <EmptyState title="No recommendations found" description="Try selecting a different product or clearing the search filter." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-[#0A1628] text-gray-200 border-b border-[#1A3A5C]">
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider">Customer ID</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider">Recommended Product</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider">Score</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider">Confidence</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider">Objective</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider">Explainability Reason</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {recommendations.map((r, i) => (
                  <tr key={i} className="hover:bg-gray-50/80 transition-colors">
                    <td className="py-3 px-4 font-mono font-semibold text-[#1A3A5C]">{r.customer_id}</td>
                    <td className="py-3 px-4 font-bold text-gray-900">{r.product_name}</td>
                    <td className="py-3 px-4 font-mono font-semibold text-[#00A896]">
                      {typeof r.recommendation_score === 'number' ? r.recommendation_score.toFixed(2) : r.recommendation_score}
                    </td>
                    <td className="py-3 px-4">
                      <Badge variant="teal">{r.recommendation_confidence || 'High'}</Badge>
                    </td>
                    <td className="py-3 px-4">
                      <Badge variant="info">{r.campaign_objective || 'Engagement'}</Badge>
                    </td>
                    <td className="py-3 px-4 text-gray-600 max-w-md">
                      {r.recommendation_reason || 'Personalized affinity match based on transaction history.'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Bar */}
        {!loading && recommendations.length > 0 && (
          <div className="p-4 border-t border-gray-100 flex items-center justify-between text-xs text-gray-500">
            <span>
              Showing {((page - 1) * pageSize) + 1} to {Math.min(page * pageSize, total)} of {total.toLocaleString()} records
            </span>
            <div className="flex items-center space-x-2">
              <button
                disabled={page <= 1}
                onClick={() => setPage(page - 1)}
                className="p-1.5 rounded border border-gray-300 disabled:opacity-40 hover:bg-gray-50 transition-colors"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="font-semibold text-gray-800">
                Page {page} of {pages}
              </span>
              <button
                disabled={page >= pages}
                onClick={() => setPage(page + 1)}
                className="p-1.5 rounded border border-gray-300 disabled:opacity-40 hover:bg-gray-50 transition-colors"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
