export type ThreatClassification =
  | 'PHISHING'
  | 'BEC'
  | 'IMPERSONATION'
  | 'FRAUD'
  | 'MALWARE'
  | 'SUSPICIOUS'
  | 'LEGITIMATE';

export type ConfidenceLevel = 'VERY_HIGH' | 'HIGH' | 'MEDIUM' | 'LOW' | 'VERY_LOW';

export type CampaignStatus =
  | 'CANDIDATE'
  | 'UNDER_REVIEW'
  | 'CONFIRMED_BY_ANALYST'
  | 'DISMISSED';

export type CaseStatus =
  | 'OPEN'
  | 'UNDER_REVIEW'
  | 'ESCALATED'
  | 'RESOLVED'
  | 'DISMISSED';

export type CasePriority = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';

export type NodeType =
  | 'EMAIL'
  | 'SENDER'
  | 'DOMAIN'
  | 'URL'
  | 'IP'
  | 'MAIL_SERVER'
  | 'ASN'
  | 'ORGANIZATION'
  | 'NAMESERVER'
  | 'LOCATION'
  | 'CAMPAIGN'
  | 'INDICATOR';

export type EdgeRelationship =
  | 'SENT_BY'
  | 'REPLY_TO'
  | 'CONTAINS_URL'
  | 'PASSED_THROUGH'
  | 'SIGNED_BY'
  | 'RESOLVES_TO'
  | 'HAS_MX'
  | 'USES_NAMESERVER'
  | 'BELONGS_TO_ASN'
  | 'OPERATED_BY'
  | 'GEOLOCATED_TO'
  | 'SHARES_INFRASTRUCTURE'
  | 'RELATED_TO'
  | 'PART_OF_CAMPAIGN';

export interface EmailSummary {
  id: string;
  subject: string;
  sender: string;
  sender_domain?: string;
  received_at: string;
  risk_score: number;
  classification: ThreatClassification;
  status: string;
  message_id?: string;
}

export interface ThreatReasoningFinding {
  id: string;
  finding: string;
  category: string;
  severity: 'HIGH' | 'MEDIUM' | 'LOW';
  evidence_reference: string;
  originating_phase: string;
}

export interface ThreatAssessment {
  risk_score: number;
  classification: ThreatClassification;
  confidence: ConfidenceLevel;
  findings: ThreatReasoningFinding[];
  summary: string;
}

export interface HeaderForensics {
  return_path?: string;
  reply_to?: string;
  from_address: string;
  to_addresses: string[];
  message_id?: string;
  spf_status: 'PASS' | 'FAIL' | 'NEUTRAL' | 'NONE';
  dkim_status: 'PASS' | 'FAIL' | 'NONE';
  dmarc_status: 'PASS' | 'FAIL' | 'NONE';
  received_hops: Array<{
    hop_index: number;
    from_server?: string;
    by_server?: string;
    ip?: string;
    timestamp?: string;
    is_suspicious?: boolean;
  }>;
}

export interface InfrastructureIndicator {
  indicator: string;
  type: 'IP' | 'DOMAIN' | 'URL';
  asn?: string;
  organization?: string;
  location?: string;
  hosting_provider?: string;
  reputation_status?: string;
  cluster_id?: string;
}

export interface GraphNode {
  id: string;
  node_type: NodeType;
  canonical_value: string;
  display_value: string;
  first_seen: string;
  last_seen: string;
  metadata?: Record<string, unknown>;
}

export interface GraphEdge {
  id: string;
  source_node_id: string;
  target_node_id: string;
  relationship_type: EdgeRelationship;
  relationship_origin: 'DIRECT' | 'INFERRED';
  confidence: number;
  strength: ConfidenceLevel;
  evidence_reference?: string;
}

export interface InvestigationGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
  center_node_id?: string;
}

export interface RelatedEmail {
  id: string;
  subject: string;
  sender: string;
  risk_score: number;
  classification: ThreatClassification;
  received_at: string;
  relationship_reasons: string[];
}

export interface CampaignCandidate {
  id: string;
  campaign_id: string;
  confidence: number;
  status: CampaignStatus;
  summary: string;
  first_seen: string;
  last_seen: string;
  email_count: number;
  clusters_count: number;
  shared_indicators: string[];
  explanation: string;
}

export interface InfrastructureCluster {
  id: string;
  cluster_key: string;
  cluster_type: string;
  confidence: number;
  first_seen: string;
  last_seen: string;
  member_count: number;
}

export interface TimelineEvent {
  id: string;
  timestamp: string;
  title: string;
  description: string;
  category: string;
  entity_reference?: string;
}

export interface Case {
  id: string;
  case_id: string;
  title: string;
  priority: CasePriority;
  status: CaseStatus;
  created_at: string;
  assigned_to: string;
  related_emails_count: number;
  campaigns_count: number;
  infrastructure_clusters_count: number;
  summary: string;
}

export interface AnalystNote {
  id: string;
  author: string;
  timestamp: string;
  content: string;
  entity_type: string;
  entity_id: string;
}

export interface GlobalSearchResults {
  emails: EmailSummary[];
  domains: Array<{ id: string; domain: string; risk: string }>;
  ips: Array<{ id: string; ip: string; org: string }>;
  cases: Case[];
  campaigns: CampaignCandidate[];
}
