export interface Customer {
  customer_id: string;
  primary_segment?: string;
  segment?: string;
  customer_persona?: string;
  retention_risk?: string;
  cross_sell_opportunity?: string;
  genai_targeting_priority?: string;
  preferred_channel?: string;
  consent_status?: string;
  [key: string]: any;
}

export interface CustomerListResponse {
  customers: Customer[];
  total: number;
  page: number;
  pages: number;
}

export interface Segment {
  segment: string;
  count: number;
  percentage: number;
  top_persona: string;
  top_retention_risk: string;
  top_product: string;
}

export interface SegmentsResponse {
  segments: Segment[];
  total_customers: number;
  persona_distribution: { persona: string; count: number }[];
  risk_distribution: { risk: string; count: number }[];
  priority_distribution: { priority: string; count: number }[];
}

export interface Recommendation {
  customer_id: string;
  product_name: string;
  recommendation_score: number | string;
  recommendation_confidence: string;
  recommendation_reason: string;
  campaign_objective: string;
}

export interface RecommendationsResponse {
  recommendations: Recommendation[];
  total: number;
  page: number;
  pages: number;
}

export interface RecommendationsSummary {
  total: number;
  customers: number;
  products: number;
  product_distribution: { product: string; count: number }[];
}

export interface CampaignContent {
  campaign_id?: number | string;
  customer_id?: string;
  product_name?: string;
  campaign_objective?: string;
  primary_segment?: string;
  customer_persona?: string;
  retention_risk?: string;
  cross_sell_opportunity?: string;
  subject?: string;
  subject_line?: string;
  headline?: string;
  greeting?: string;
  body?: string;
  email_body?: string;
  cta?: string;
  call_to_action?: string;
  closing?: string;
  sms?: string;
  status?: string;
  compliance_score?: number;
  generation_mode?: string;
  variant_rationale?: string;
  variant_strength?: string;
  [key: string]: any;
}

export interface GenerateCampaignResponse {
  campaign: CampaignContent;
  campaign_id: number;
  variant_a?: CampaignContent;
  variant_b?: CampaignContent;
}

export interface ComplianceResult {
  score: number;
  status: "Approved" | "Needs Review" | "Rejected";
  issues: string[];
  flagged_phrases: string[];
  can_approve: boolean;
}

export interface DeliveryLog {
  id: number;
  campaign_id: number;
  channel: string;
  recipient: string;
  status: string;
  provider_message: string;
  created_at: string;
}

export interface AnalyticsSummary {
  total_customers: number;
  active_segments: number;
  total_recommendations: number;
  total_campaigns: number;
  approved_campaigns: number;
  messages_sent: number;
  ab_variants: number;
  delivery_records: number;
  campaign_status_distribution: Record<string, number>;
  segment_distribution: { segment: string; count: number }[];
  product_distribution: { product: string; count: number }[];
  ab_summary: {
    a_wins?: number;
    b_wins?: number;
    ties?: number;
    top_strategy?: string;
  };
}

export interface ABAnalytics {
  a_wins: number;
  b_wins: number;
  ties: number;
  winning_variant: string;
  top_strategy: string;
  avg_score_a: number;
  avg_score_b: number;
  score_gap: number;
  objectives: { objective: string; count: number }[];
  products: { product: string; count: number }[];
  total: number;
}
