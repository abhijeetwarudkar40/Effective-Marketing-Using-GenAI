import React, { useEffect, useState } from 'react';
import { Search, Filter, Eye, ShieldCheck, ChevronLeft, ChevronRight, User } from 'lucide-react';
import { getCustomers, getCustomerSegmentsList, getCustomerRecommendations } from '../services/api';
import { Customer } from '../types';
import { PageHeader } from '../components/common/PageHeader';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';

export const CustomersPage: React.FC = () => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [segments, setSegments] = useState<string[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [pageSize] = useState(25);
  const [search, setSearch] = useState('');
  const [selectedSegment, setSelectedSegment] = useState('All');
  const [loading, setLoading] = useState(true);

  // Customer 360 modal
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [customerRecs, setCustomerRecs] = useState<any[]>([]);
  const [loadingRecs, setLoadingRecs] = useState(false);

  useEffect(() => {
    const loadSegments = async () => {
      try {
        const segs = await getCustomerSegmentsList();
        setSegments(segs);
      } catch (err) {
        console.error(err);
      }
    };
    loadSegments();
  }, []);

  const loadCustomerData = async () => {
    try {
      setLoading(true);
      const res = await getCustomers(page, pageSize, search, selectedSegment);
      setCustomers(res.customers);
      setTotal(res.total);
      setPages(res.pages);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCustomerData();
  }, [page, selectedSegment]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    loadCustomerData();
  };

  const handleView360 = async (customer: Customer) => {
    setSelectedCustomer(customer);
    try {
      setLoadingRecs(true);
      const recs = await getCustomerRecommendations(customer.customer_id);
      setCustomerRecs(recs);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingRecs(false);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Customer 360°"
        subtitle="Explore customer segmentation, personas, retention risks, and individual Customer 360° banking profiles."
      />

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <form onSubmit={handleSearchSubmit} className="flex-1 flex items-center space-x-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by Customer ID, Persona or Segment..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 text-xs border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#00A896]/20 focus:border-[#00A896]"
            />
          </div>
          <button
            type="submit"
            className="bg-[#1A3A5C] text-white px-4 py-2 rounded-lg text-xs font-semibold hover:bg-[#0A1628] transition-colors"
          >
            Search
          </button>
        </form>

        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-500" />
            <span className="text-xs font-semibold text-gray-700">Segment:</span>
          </div>
          <select
            value={selectedSegment}
            onChange={(e) => {
              setSelectedSegment(e.target.value);
              setPage(1);
            }}
            className="text-xs border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#00A896]/20 focus:border-[#00A896]"
          >
            <option value="All">All Segments ({total})</option>
            {segments.map((seg) => (
              <option key={seg} value={seg}>
                {seg}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Customer Data Table */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-xs overflow-hidden">
        {loading ? (
          <LoadingSpinner message="Querying customer profiles..." />
        ) : customers.length === 0 ? (
          <EmptyState title="No customers found" description="Try modifying your search or filter parameters." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-[#0A1628] text-gray-200 border-b border-[#1A3A5C]">
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider">Customer ID</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider">Primary Segment</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider">Persona</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider">Retention Risk</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider">Cross-Sell Opportunity</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {customers.map((c) => {
                  const riskVariant =
                    c.retention_risk?.toLowerCase().includes('high')
                      ? 'danger'
                      : c.retention_risk?.toLowerCase().includes('medium') || c.retention_risk?.toLowerCase().includes('moderate')
                      ? 'warning'
                      : 'success';

                  return (
                    <tr key={c.customer_id} className="hover:bg-gray-50/80 transition-colors">
                      <td className="py-3 px-4 font-mono font-semibold text-[#1A3A5C]">
                        {c.customer_id}
                      </td>
                      <td className="py-3 px-4 font-medium text-gray-800">
                        {c.primary_segment || c.segment || '—'}
                      </td>
                      <td className="py-3 px-4 text-gray-600">
                        {c.customer_persona || '—'}
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant={riskVariant}>{c.retention_risk || 'Normal'}</Badge>
                      </td>
                      <td className="py-3 px-4 text-gray-600">
                        {c.cross_sell_opportunity || '—'}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={() => handleView360(c)}
                          className="inline-flex items-center space-x-1 px-2.5 py-1 rounded bg-[#00A896]/10 text-[#007A6C] hover:bg-[#00A896]/20 font-semibold text-[11px] transition-colors"
                        >
                          <Eye className="w-3.5 h-3.5" />
                          <span>Customer 360°</span>
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Bar */}
        {!loading && customers.length > 0 && (
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

      {/* Customer 360 Modal */}
      {selectedCustomer && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-fadeIn">
          <div className="bg-white rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto shadow-2xl border border-gray-200">
            <div className="bg-[#0A1628] text-white p-6 rounded-t-2xl flex items-center justify-between border-b border-[#1A3A5C]">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-full bg-[#1A3A5C] border border-[#00A896]/40 flex items-center justify-center text-[#00A896]">
                  <User className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Customer 360° Profile</h3>
                  <p className="text-xs text-gray-400 font-mono">ID: {selectedCustomer.customer_id}</p>
                </div>
              </div>
              <button
                onClick={() => setSelectedCustomer(null)}
                className="text-gray-400 hover:text-white text-lg font-bold p-1 rounded hover:bg-[#1A3A5C]"
              >
                ✕
              </button>
            </div>

            <div className="p-6 space-y-6">
              {/* Profile Overview */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-3">Profile Attributes</h4>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  <div className="bg-[#F8FAFC] p-3 rounded-lg border border-gray-100">
                    <span className="text-[10px] uppercase font-semibold text-gray-400">Primary Segment</span>
                    <p className="text-xs font-bold text-[#1A3A5C] mt-0.5">{selectedCustomer.primary_segment || selectedCustomer.segment || '—'}</p>
                  </div>
                  <div className="bg-[#F8FAFC] p-3 rounded-lg border border-gray-100">
                    <span className="text-[10px] uppercase font-semibold text-gray-400">Customer Persona</span>
                    <p className="text-xs font-bold text-gray-800 mt-0.5">{selectedCustomer.customer_persona || '—'}</p>
                  </div>
                  <div className="bg-[#F8FAFC] p-3 rounded-lg border border-gray-100">
                    <span className="text-[10px] uppercase font-semibold text-gray-400">Retention Risk</span>
                    <p className="text-xs font-bold text-gray-800 mt-0.5">{selectedCustomer.retention_risk || '—'}</p>
                  </div>
                  <div className="bg-[#F8FAFC] p-3 rounded-lg border border-gray-100 col-span-2 sm:col-span-3">
                    <span className="text-[10px] uppercase font-semibold text-gray-400">Cross-Sell Opportunity</span>
                    <p className="text-xs font-medium text-gray-700 mt-0.5">{selectedCustomer.cross_sell_opportunity || '—'}</p>
                  </div>
                </div>
              </div>

              {/* Recommendations for this customer */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-3">Model Product Recommendations</h4>
                {loadingRecs ? (
                  <LoadingSpinner message="Loading recommendations..." className="py-6" />
                ) : customerRecs.length === 0 ? (
                  <p className="text-xs text-gray-500 bg-gray-50 p-4 rounded-lg">No direct recommendations found for this customer.</p>
                ) : (
                  <div className="space-y-3">
                    {customerRecs.map((r, i) => (
                      <div key={i} className="p-4 rounded-xl border border-gray-200 bg-[#F8FAFC] flex flex-col justify-between">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-sm text-[#0A1628]">{r.product_name}</span>
                          <Badge variant="teal">Score: {r.recommendation_score || 'N/A'}</Badge>
                        </div>
                        {r.recommendation_reason && (
                          <p className="text-xs text-gray-600 mt-2 leading-relaxed">
                            <strong>Reason:</strong> {r.recommendation_reason}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div className="p-4 bg-gray-50 border-t border-gray-200 rounded-b-2xl flex justify-end">
              <button
                onClick={() => setSelectedCustomer(null)}
                className="bg-gray-200 hover:bg-gray-300 text-gray-800 px-4 py-2 rounded-lg text-xs font-semibold transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
