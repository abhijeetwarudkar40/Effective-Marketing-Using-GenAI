import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Sparkles,
  Mail,
  MessageSquare,
  ShieldCheck,
  Edit3,
  Save,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  RefreshCw,
  User,
  Sliders
} from 'lucide-react';
import { getCampaignContext, generateCampaign, updateCampaign } from '../services/api';
import { CampaignContent } from '../types';
import { PageHeader } from '../components/common/PageHeader';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export const CampaignStudioPage: React.FC = () => {
  const navigate = useNavigate();

  // Selection inputs
  const [customers, setCustomers] = useState<string[]>([]);
  const [selectedCustomerId, setSelectedCustomerId] = useState<string>('');
  const [products, setProducts] = useState<string[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<string>('');
  const [contextData, setContextData] = useState<any>({});
  const [language, setLanguage] = useState('English');
  const [tone, setTone] = useState('Professional');

  // Generation state
  const [generating, setGenerating] = useState(false);
  const [generatedCampaign, setGeneratedCampaign] = useState<CampaignContent | null>(null);
  const [campaignId, setCampaignId] = useState<number | null>(null);
  const [variantA, setVariantA] = useState<CampaignContent | null>(null);
  const [variantB, setVariantB] = useState<CampaignContent | null>(null);

  // Tabs & Editing
  const [activeTab, setActiveTab] = useState<'email' | 'sms' | 'ab'>('email');
  const [isEditing, setIsEditing] = useState(false);
  const [editSubject, setEditSubject] = useState('');
  const [editBody, setEditBody] = useState('');
  const [editCta, setEditCta] = useState('');
  const [editSms, setEditSms] = useState('');
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Error/Status message
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const [contextByProduct, setContextByProduct] = useState<Record<string, any>>({});
  const [recommendedProducts, setRecommendedProducts] = useState<string[]>([]);

  // Load initial customer list
  useEffect(() => {
    const loadContext = async () => {
      try {
        const data = await getCampaignContext();
        setCustomers(data.customers);
        if (data.customers.length > 0) {
          const firstCustomer = data.customers[0];
          setSelectedCustomerId(firstCustomer);
          loadCustomerDetails(firstCustomer);
        }
      } catch (err: any) {
        console.error(err);
      }
    };
    loadContext();
  }, []);

  const loadCustomerDetails = async (cid: string, chosenProduct?: string) => {
    try {
      const data = await getCampaignContext(cid, chosenProduct);
      setProducts(data.products || []);
      setRecommendedProducts(data.recommended_products || []);
      setContextByProduct(data.context_by_product || {});

      const activeProd = chosenProduct || (data.products && data.products.length > 0 ? data.products[0] : '');
      setSelectedProduct(activeProd);

      if (data.context_by_product && data.context_by_product[activeProd]) {
        setContextData(data.context_by_product[activeProd]);
      } else {
        setContextData(data.context || {});
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleCustomerChange = (cid: string) => {
    setSelectedCustomerId(cid);
    loadCustomerDetails(cid);
  };

  const handleProductChange = (prod: string) => {
    setSelectedProduct(prod);
    if (contextByProduct[prod]) {
      setContextData(contextByProduct[prod]);
    } else {
      loadCustomerDetails(selectedCustomerId, prod);
    }
  };

  const handleGenerate = async () => {
    if (!selectedCustomerId || !selectedProduct) return;
    try {
      setGenerating(true);
      setErrorMsg(null);
      setSaveSuccess(false);

      const res = await generateCampaign({
        customer_id: selectedCustomerId,
        product: selectedProduct,
        language,
        tone,
      });

      setGeneratedCampaign(res.campaign);
      setCampaignId(res.campaign_id);
      setVariantA(res.variant_a || null);
      setVariantB(res.variant_b || null);

      // Populate edit fields
      setEditSubject(res.campaign.subject || res.campaign.subject_line || '');
      setEditBody(res.campaign.email_body || res.campaign.body || '');
      setEditCta(res.campaign.cta || res.campaign.call_to_action || '');
      setEditSms(res.campaign.sms || '');

      // Store in localStorage for workflow persistence
      localStorage.setItem('bankwise_active_campaign', JSON.stringify(res.campaign));
      localStorage.setItem('bankwise_active_campaign_id', String(res.campaign_id));
      if (res.variant_a) localStorage.setItem('bankwise_active_variant_a', JSON.stringify(res.variant_a));
      if (res.variant_b) localStorage.setItem('bankwise_active_variant_b', JSON.stringify(res.variant_b));
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || err.message || 'Generation failed');
    } finally {
      setGenerating(false);
    }
  };

  const handleSaveEdit = async () => {
    if (!campaignId) return;
    try {
      await updateCampaign(campaignId, {
        subject: editSubject,
        email_body: editBody,
      });

      if (generatedCampaign) {
        const updated = {
          ...generatedCampaign,
          subject: editSubject,
          subject_line: editSubject,
          email_body: editBody,
          body: editBody,
          cta: editCta,
          sms: editSms,
        };
        setGeneratedCampaign(updated);
        localStorage.setItem('bankwise_active_campaign', JSON.stringify(updated));
      }
      setIsEditing(false);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err: any) {
      setErrorMsg('Failed to save edited campaign');
    }
  };

  const proceedToCompliance = () => {
    navigate('/compliance');
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="GenAI Campaign Studio"
        subtitle="AI-powered hyper-personalized email & SMS campaign generator using customer profiles and recommendation rationale."
      />

      {errorMsg && (
        <div className="p-4 bg-red-50 text-red-700 rounded-xl border border-red-200 text-xs flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-red-500" />
            <span>{errorMsg}</span>
          </div>
          <button onClick={() => setErrorMsg(null)} className="font-bold">✕</button>
        </div>
      )}

      {/* Campaign Configuration Card */}
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-xs space-y-6">
        <div className="border-b border-gray-100 pb-4">
          <h3 className="text-sm font-bold text-[#0A1628] flex items-center space-x-2">
            <Sliders className="w-4 h-4 text-[#00A896]" />
            <span>1. Customer & Campaign Settings</span>
          </h3>
          <p className="text-xs text-gray-500 mt-1">Select recipient and tone to initialize GenAI generation prompt.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Customer Dropdown */}
          <div>
            <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
              Select Customer
            </label>
            <select
              value={selectedCustomerId}
              onChange={(e) => handleCustomerChange(e.target.value)}
              className="w-full text-xs font-mono border border-gray-300 rounded-lg p-2.5 bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#00A896]/20 focus:border-[#00A896]"
            >
              {customers.map((cid) => (
                <option key={cid} value={cid}>
                  {cid}
                </option>
              ))}
            </select>
          </div>

          {/* Recommended Product with multiple categorized options */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider">
                Product Selection
              </label>
              {recommendedProducts.includes(selectedProduct) && (
                <span className="text-[10px] text-[#00A896] font-bold">★ ML Scored</span>
              )}
            </div>
            <select
              value={selectedProduct}
              onChange={(e) => handleProductChange(e.target.value)}
              className="w-full text-xs border border-gray-300 rounded-lg p-2.5 bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#00A896]/20 focus:border-[#00A896]"
            >
              {recommendedProducts.length > 0 && (
                <optgroup label="⭐ Model Recommended Products">
                  {recommendedProducts.map((p) => (
                    <option key={`rec-${p}`} value={p}>
                      ★ {p} (Recommended)
                    </option>
                  ))}
                </optgroup>
              )}
              <optgroup label="🏦 Full Banking Product Catalog">
                {products
                  .filter((p) => !recommendedProducts.includes(p))
                  .map((p) => (
                    <option key={`cat-${p}`} value={p}>
                      {p}
                    </option>
                  ))}
              </optgroup>
            </select>
          </div>

          {/* Language */}
          <div>
            <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
              Language
            </label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full text-xs border border-gray-300 rounded-lg p-2.5 bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#00A896]/20 focus:border-[#00A896]"
            >
              <option value="English">English</option>
              <option value="Hindi">Hindi (हिंदी)</option>
              <option value="Marathi">Marathi (मराठी)</option>
            </select>
          </div>

          {/* Tone */}
          <div>
            <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
              Brand Tone
            </label>
            <select
              value={tone}
              onChange={(e) => setTone(e.target.value)}
              className="w-full text-xs border border-gray-300 rounded-lg p-2.5 bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#00A896]/20 focus:border-[#00A896]"
            >
              <option value="Professional">Professional (Corporate Banking)</option>
              <option value="Friendly">Friendly (Retail & Wealth)</option>
              <option value="Persuasive">Persuasive (Cross-Sell / Retention)</option>
            </select>
          </div>
        </div>

        {/* Selected Customer Context Badge Bar */}
        {contextData && Object.keys(contextData).length > 0 && (
          <div className="bg-[#F8FAFC] p-3 rounded-lg border border-gray-100 flex flex-wrap items-center gap-4 text-xs">
            <span className="text-gray-500 font-semibold">Customer Context:</span>
            <span className="text-gray-700">Segment: <strong className="text-[#0A1628]">{contextData.primary_segment || contextData.segment || 'Core'}</strong></span>
            <span className="text-gray-700">Persona: <strong className="text-[#0A1628]">{contextData.customer_persona || 'Customer'}</strong></span>
            <span className="text-gray-700">Risk: <strong className="text-[#0A1628]">{contextData.retention_risk || 'Low Risk'}</strong></span>
            <span className="text-gray-700">Objective: <strong className="text-[#00A896]">{contextData.campaign_objective || 'Engagement'}</strong></span>
          </div>
        )}

        {/* Generate Button */}
        <div>
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="w-full py-3 bg-gradient-to-r from-[#00A896] to-[#1A3A5C] text-white font-bold text-sm rounded-lg shadow-sm hover:opacity-95 transition-all flex items-center justify-center space-x-2 disabled:opacity-50"
          >
            {generating ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Executing Gemini 3.6 Flash Generation...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Generate Hyper-Personalized Campaign</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Generated Content Preview & Workspace */}
      {generatedCampaign && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-xs overflow-hidden">
          {/* Header & Tabs */}
          <div className="bg-[#0A1628] text-white p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center space-x-3">
              <span className="text-xs font-mono bg-[#1A3A5C] text-[#00A896] px-2 py-1 rounded border border-[#00A896]/30">
                ID: #{campaignId || 'GEN-01'}
              </span>
              <span className="text-xs text-gray-300">
                Mode: <strong>{generatedCampaign.generation_mode || 'Gemini 3.6 Flash'}</strong>
              </span>
            </div>

            <div className="flex items-center space-x-2">
              <div className="flex bg-[#1A3A5C] p-1 rounded-lg">
                <button
                  onClick={() => setActiveTab('email')}
                  className={`px-3 py-1 text-xs font-semibold rounded-md flex items-center space-x-1.5 transition-all ${
                    activeTab === 'email' ? 'bg-[#00A896] text-white shadow-xs' : 'text-gray-300 hover:text-white'
                  }`}
                >
                  <Mail className="w-3.5 h-3.5" />
                  <span>Email</span>
                </button>
                <button
                  onClick={() => setActiveTab('sms')}
                  className={`px-3 py-1 text-xs font-semibold rounded-md flex items-center space-x-1.5 transition-all ${
                    activeTab === 'sms' ? 'bg-[#00A896] text-white shadow-xs' : 'text-gray-300 hover:text-white'
                  }`}
                >
                  <MessageSquare className="w-3.5 h-3.5" />
                  <span>SMS</span>
                </button>
              </div>

              {!isEditing ? (
                <button
                  onClick={() => setIsEditing(true)}
                  className="px-3 py-1.5 bg-[#1A3A5C] hover:bg-[#2C5F8A] text-white text-xs font-semibold rounded-lg flex items-center space-x-1 transition-colors"
                >
                  <Edit3 className="w-3.5 h-3.5" />
                  <span>Edit Content</span>
                </button>
              ) : (
                <button
                  onClick={handleSaveEdit}
                  className="px-3 py-1.5 bg-[#2E7D32] hover:bg-[#256629] text-white text-xs font-semibold rounded-lg flex items-center space-x-1 transition-colors"
                >
                  <Save className="w-3.5 h-3.5" />
                  <span>Save Changes</span>
                </button>
              )}
            </div>
          </div>

          {saveSuccess && (
            <div className="bg-green-50 text-green-700 text-xs px-4 py-2 flex items-center space-x-2 border-b border-green-200">
              <CheckCircle2 className="w-4 h-4 text-green-600" />
              <span>Campaign updated successfully in database!</span>
            </div>
          )}

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'email' ? (
              <div className="space-y-4">
                {/* Subject */}
                <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">Email Subject</label>
                  {isEditing ? (
                    <input
                      type="text"
                      value={editSubject}
                      onChange={(e) => setEditSubject(e.target.value)}
                      className="w-full text-sm font-semibold border border-gray-300 rounded-lg p-2.5 focus:outline-none focus:ring-2 focus:ring-[#00A896]/20 focus:border-[#00A896]"
                    />
                  ) : (
                    <div className="p-3 bg-[#E8F1FF] text-[#0056B3] font-bold text-sm rounded-lg border border-[#BEE3F8]">
                      {generatedCampaign.subject || generatedCampaign.subject_line}
                    </div>
                  )}
                </div>

                {/* Headline */}
                {generatedCampaign.headline && (
                  <div>
                    <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">Headline</label>
                    <h4 className="text-base font-bold text-gray-900">{generatedCampaign.headline}</h4>
                  </div>
                )}

                {/* Email Body */}
                <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">Message Content</label>
                  {isEditing ? (
                    <textarea
                      rows={6}
                      value={editBody}
                      onChange={(e) => setEditBody(e.target.value)}
                      className="w-full text-xs font-normal border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-[#00A896]/20 focus:border-[#00A896] leading-relaxed"
                    />
                  ) : (
                    <div className="p-4 bg-[#F8FAFC] border border-gray-200 rounded-lg text-xs text-gray-800 leading-relaxed whitespace-pre-line">
                      {generatedCampaign.greeting && <p className="mb-2 font-medium">{generatedCampaign.greeting}</p>}
                      <p>{generatedCampaign.email_body || generatedCampaign.body}</p>
                      {generatedCampaign.closing && <p className="mt-3 text-gray-600 italic whitespace-pre-line">{generatedCampaign.closing}</p>}
                    </div>
                  )}
                </div>

                {/* CTA Box */}
                <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">Call to Action</label>
                  {isEditing ? (
                    <input
                      type="text"
                      value={editCta}
                      onChange={(e) => setEditCta(e.target.value)}
                      className="w-full text-xs font-semibold border border-gray-300 rounded-lg p-2.5 focus:outline-none focus:ring-2 focus:ring-[#00A896]/20 focus:border-[#00A896]"
                    />
                  ) : (
                    <div className="inline-block px-4 py-2 bg-[#1A3A5C] text-white font-bold text-xs rounded-lg shadow-xs">
                      {generatedCampaign.cta || generatedCampaign.call_to_action || 'Explore Product'}
                    </div>
                  )}
                </div>
              </div>
            ) : (
              /* SMS Tab */
              <div className="space-y-4 max-w-lg">
                <div className="flex items-center justify-between">
                  <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider">SMS Message Body</label>
                  <span className="text-xs font-mono font-semibold text-gray-600">
                    Length: {(isEditing ? editSms.length : (generatedCampaign.sms?.length || 0))} / 160 chars
                  </span>
                </div>

                {isEditing ? (
                  <textarea
                    rows={4}
                    value={editSms}
                    onChange={(e) => setEditSms(e.target.value)}
                    className="w-full text-xs font-normal border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-[#00A896]/20 focus:border-[#00A896]"
                  />
                ) : (
                  <div className="p-4 bg-gray-50 border border-gray-200 rounded-xl text-xs text-gray-800 font-mono leading-relaxed">
                    {generatedCampaign.sms || `${generatedCampaign.headline} ${generatedCampaign.email_body} ${generatedCampaign.cta}`}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Workflow Footer */}
          <div className="p-4 bg-gray-50 border-t border-gray-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center space-x-2 text-xs text-gray-500">
              <ShieldCheck className="w-4 h-4 text-[#00A896]" />
              <span>Campaign saved as draft in SQLite. Generate tailored graphic banners or proceed to compliance.</span>
            </div>

            <div className="flex items-center space-x-3">
              <button
                onClick={() => navigate('/creative-studio')}
                className="bg-[#1A3A5C] hover:bg-[#0A1628] text-white font-bold text-xs px-5 py-2.5 rounded-lg shadow-xs transition-colors flex items-center justify-center space-x-2"
              >
                <span>Proceed to Creative Studio</span>
                <ArrowRight className="w-4 h-4 text-[#00A896]" />
              </button>

              <button
                onClick={proceedToCompliance}
                className="bg-[#00A896] hover:bg-[#008f80] text-white font-bold text-xs px-5 py-2.5 rounded-lg shadow-xs transition-colors flex items-center justify-center space-x-2"
              >
                <span>Compliance & Approval</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
