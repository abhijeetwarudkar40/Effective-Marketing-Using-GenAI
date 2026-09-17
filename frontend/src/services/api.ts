import axios from 'axios';
import {
  CustomerListResponse,
  Customer,
  SegmentsResponse,
  RecommendationsResponse,
  RecommendationsSummary,
  GenerateCampaignResponse,
  CampaignContent,
  ComplianceResult,
  DeliveryLog,
  AnalyticsSummary,
  ABAnalytics
} from '../types';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getHealth = async () => {
  const res = await api.get('/health');
  return res.data;
};

// Customers
export const getCustomers = async (page = 1, pageSize = 50, search = '', segment = '') => {
  const params: any = { page, page_size: pageSize };
  if (search) params.search = search;
  if (segment && segment !== 'All') params.segment = segment;
  const res = await api.get<CustomerListResponse>('/customers', { params });
  return res.data;
};

export const getCustomerSegmentsList = async () => {
  const res = await api.get<{ segments: string[] }>('/customers/segments-list');
  return res.data.segments;
};

export const getCustomer = async (id: string) => {
  const res = await api.get<{ customer: Customer | null }>(`/customers/${id}`);
  return res.data.customer;
};

// Segments
export const getSegments = async () => {
  const res = await api.get<SegmentsResponse>('/segments');
  return res.data;
};

// Recommendations
export const getRecommendations = async (page = 1, pageSize = 50, customerId = '', product = '') => {
  const params: any = { page, page_size: pageSize };
  if (customerId) params.customer_id = customerId;
  if (product && product !== 'All') params.product = product;
  const res = await api.get<RecommendationsResponse>('/recommendations', { params });
  return res.data;
};

export const getRecommendationProductsList = async () => {
  const res = await api.get<{ products: string[] }>('/recommendations/products-list');
  return res.data.products;
};

export const getRecommendationsSummary = async () => {
  const res = await api.get<RecommendationsSummary>('/recommendations/summary');
  return res.data;
};

export const getCustomerRecommendations = async (customerId: string) => {
  const res = await api.get<{ recommendations: any[] }>(`/recommendations/${customerId}`);
  return res.data.recommendations;
};

// Campaigns
export const getCampaignContext = async (customerId?: string, product?: string) => {
  const params: any = {};
  if (customerId) params.customer_id = customerId;
  if (product) params.product = product;
  const res = await api.get<{
    customers: string[];
    products: string[];
    recommended_products?: string[];
    context_by_product?: Record<string, any>;
    context?: any;
  }>('/campaigns/context', { params });
  return res.data;
};

export const generateCampaign = async (payload: {
  customer_id: string;
  product: string;
  language?: string;
  tone?: string;
}) => {
  const res = await api.post<GenerateCampaignResponse>('/campaigns/generate', payload);
  return res.data;
};

export const getCampaigns = async () => {
  const res = await api.get<{ campaigns: CampaignContent[] }>('/campaigns');
  return res.data.campaigns;
};

export const updateCampaign = async (campaignId: number, data: { subject?: string; email_body?: string }) => {
  const res = await api.put(`/campaigns/${campaignId}`, data);
  return res.data;
};

export const getABVariantsForCustomer = async (customerId: string) => {
  const res = await api.get<{ variant_a: any; variant_b: any }>(`/campaigns/ab-variants/${customerId}`);
  return res.data;
};

// Creative Studio
export const generateCreatives = async (payload: {
  customer_id?: string;
  primary_segment?: string;
  product_name?: string;
  campaign_objective?: string;
  headline?: string;
  email_body?: string;
  cta?: string;
  option?: number;
}) => {
  const res = await api.post<{
    banners: {
      option: number;
      image_base64: string;
      metadata: any;
    }[];
  }>('/creative/generate', payload);
  return res.data.banners;
};

export const approveCreative = async (payload: {
  campaign_id: string;
  option: number;
  image_base64: string;
  metadata: any;
}) => {
  const res = await api.post('/creative/approve', payload);
  return res.data;
};

export const getApprovedCreative = async (campaignId: number | string) => {
  const res = await api.get<{ has_creative: boolean; image_base64: string | null }>(
    `/campaigns/${campaignId}/approved-creative`
  );
  return res.data;
};

// Compliance
export const checkCompliance = async (campaign: any, consentConfirmed: boolean) => {
  const res = await api.post<ComplianceResult>('/compliance/check', {
    campaign,
    consent_confirmed: consentConfirmed,
  });
  return res.data;
};

// Approvals
export const sendForReview = async (campaignId: number, notes = '') => {
  const res = await api.post(`/campaigns/${campaignId}/review`, { notes });
  return res.data;
};

export const approveCampaign = async (campaignId: number, complianceScore?: number, notes = '') => {
  const res = await api.post(`/campaigns/${campaignId}/approve`, {
    compliance_score: complianceScore,
    notes: notes || 'Human-in-the-loop approval granted',
  });
  return res.data;
};

// Delivery
export const sendEmail = async (
  campaignId: number,
  campaign: any,
  recipient: string,
  imageBase64?: string
) => {
  const res = await api.post<{ status: string; message: string; image_attached?: boolean }>(
    `/campaigns/${campaignId}/send-email`,
    {
      campaign_id: campaignId,
      campaign,
      recipient,
      image_base64: imageBase64,
    }
  );
  return res.data;
};

export const sendSms = async (campaignId: number, campaign: any, recipient: string) => {
  const res = await api.post<{ status: string; message: string; sms_text?: string }>(`/campaigns/${campaignId}/send-sms`, {
    campaign_id: campaignId,
    campaign,
    recipient,
  });
  return res.data;
};

export const getDeliveries = async () => {
  const res = await api.get<{ deliveries: DeliveryLog[] }>('/deliveries');
  return res.data.deliveries;
};

// Analytics & A/B Testing
export const getAnalyticsSummary = async () => {
  const res = await api.get<AnalyticsSummary>('/analytics/summary');
  return res.data;
};

export const getABTestingAnalytics = async () => {
  const res = await api.get<ABAnalytics>('/ab-testing/analytics');
  return res.data;
};

export const getABTestingVariants = async (page = 1, pageSize = 20) => {
  const res = await api.get<{ variants: any[]; total: number }>('/ab-testing/variants', {
    params: { page, page_size: pageSize },
  });
  return res.data;
};
