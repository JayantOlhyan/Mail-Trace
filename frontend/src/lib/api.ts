import {
  EmailSummary,
  ThreatAssessment,
  HeaderForensics,
  InfrastructureIndicator,
  InvestigationGraph,
  CampaignCandidate,
  InfrastructureCluster,
  TimelineEvent,
  Case,
  AnalystNote,
  GlobalSearchResults,
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

async function fetcher<T>(endpoint: string, options?: RequestInit): Promise<T> {
  try {
    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    });
    if (!res.ok) {
      throw new Error(`API error ${res.status}: ${res.statusText}`);
    }
    return await res.json();
  } catch (err) {
    console.warn(`Backend request to ${endpoint} failed, falling back to operational demo provider`, err);
    return getMockFallbackData<T>(endpoint, options);
  }
}

// Operational fallback data generator for SIH demo / offline environment
function getMockFallbackData<T>(endpoint: string, options?: RequestInit): T {
  if (endpoint === '/metrics' || endpoint.startsWith('/dashboard')) {
    return {
      threats_detected: 183,
      high_risk: 24,
      open_cases: 12,
      campaign_candidates: 7,
      infrastructure_clusters: 15,
    } as unknown as T;
  }

  if (endpoint.startsWith('/emails')) {
    if (endpoint === '/emails' || endpoint.includes('?')) {
      return [
        {
          id: 'EML-2026-8801',
          subject: 'URGENT: Payroll Verification & Direct Deposit Update Required',
          sender: 'payroll-update@paypa1-support.com',
          sender_domain: 'paypa1-support.com',
          received_at: '2026-08-30T14:23:10Z',
          risk_score: 91,
          classification: 'PHISHING',
          status: 'UNDER_INVESTIGATION',
          message_id: '<202608301423.8801@paypa1-support.com>',
        },
        {
          id: 'EML-2026-8802',
          subject: 'Wire Transfer Authorization for Q3 Vendor Invoice #8849',
          sender: 'ceo-office@exec-management-corp.net',
          sender_domain: 'exec-management-corp.net',
          received_at: '2026-08-30T12:10:00Z',
          risk_score: 87,
          classification: 'BEC',
          status: 'OPEN',
          message_id: '<202608301210.8802@exec-management-corp.net>',
        },
        {
          id: 'EML-2026-8803',
          subject: 'Security Alert: Password Reset Required Immediately',
          sender: 'security@auth-services-portal.org',
          sender_domain: 'auth-services-portal.org',
          received_at: '2026-08-29T18:45:22Z',
          risk_score: 95,
          classification: 'IMPERSONATION',
          status: 'ESCALATED',
          message_id: '<202608291845.8803@auth-services-portal.org>',
        },
        {
          id: 'EML-2026-8804',
          subject: 'Quarterly Team All-Hands Agenda & Slide Deck',
          sender: 'hr@legitimate-company.com',
          sender_domain: 'legitimate-company.com',
          received_at: '2026-08-29T10:15:00Z',
          risk_score: 12,
          classification: 'LEGITIMATE',
          status: 'CLOSED',
          message_id: '<202608291015.8804@legitimate-company.com>',
        },
      ] as unknown as T;
    }

    const emailId = endpoint.split('/')[2];

    if (endpoint.endsWith('/threat')) {
      return {
        risk_score: 91,
        classification: 'PHISHING',
        confidence: 'HIGH',
        summary: 'Deceptive lookalike domain registered 2 days ago requesting urgent credential validation via unauthenticated relay server in suspicious ASN.',
        findings: [
          {
            id: 'FND-001',
            finding: 'Domain paypa1-support.com is a deceptive lookalike of legitimate brand paypal.com (Levenshtein distance: 1).',
            category: 'Lookalike Domain',
            severity: 'HIGH',
            evidence_reference: 'RFC5322 From: header evaluation',
            originating_phase: 'Phase 3',
          },
          {
            id: 'FND-002',
            finding: 'SPF verification failed (softfail) for IP 203.0.113.10.',
            category: 'Authentication Failure',
            severity: 'HIGH',
            evidence_reference: 'Received SPF header line 2',
            originating_phase: 'Phase 2',
          },
          {
            id: 'FND-003',
            finding: 'DKIM signature missing or failed validation.',
            category: 'Authentication Failure',
            severity: 'MEDIUM',
            evidence_reference: 'Header Authentication-Results',
            originating_phase: 'Phase 2',
          },
          {
            id: 'FND-004',
            finding: 'Embedded hyperlink targets credential harvester form: http://verify-login.paypa1-support.com/auth.',
            category: 'Credential Harvesting',
            severity: 'HIGH',
            evidence_reference: 'MIME HTML Body AST parsing',
            originating_phase: 'Phase 3',
          },
        ],
      } as unknown as T;
    }

    if (endpoint.endsWith('/forensics')) {
      return {
        return_path: 'bounces@paypa1-support.com',
        reply_to: 'harvest-collector@random-drop-domain.com',
        from_address: 'payroll-update@paypa1-support.com',
        to_addresses: ['employee@target-org.com'],
        message_id: '<202608301423.8801@paypa1-support.com>',
        spf_status: 'FAIL',
        dkim_status: 'FAIL',
        dmarc_status: 'FAIL',
        received_hops: [
          {
            hop_index: 1,
            from_server: 'mail.paypa1-support.com',
            by_server: 'mta-01.relay-host.net',
            ip: '203.0.113.10',
            timestamp: '2026-08-30T14:22:58Z',
            is_suspicious: true,
          },
          {
            hop_index: 2,
            from_server: 'mta-01.relay-host.net',
            by_server: 'mx.target-org.com',
            ip: '198.51.100.45',
            timestamp: '2026-08-30T14:23:05Z',
            is_suspicious: false,
          },
        ],
      } as unknown as T;
    }

    if (endpoint.endsWith('/graph')) {
      return {
        center_node_id: `NODE-${emailId}`,
        nodes: [
          {
            id: `NODE-${emailId}`,
            node_type: 'EMAIL',
            canonical_value: emailId,
            display_value: 'URGENT: Payroll Verification',
            first_seen: '2026-08-30T14:23:10Z',
            last_seen: '2026-08-30T14:23:10Z',
          },
          {
            id: 'NODE-SENDER-01',
            node_type: 'SENDER',
            canonical_value: 'payroll-update@paypa1-support.com',
            display_value: 'payroll-update@paypa1-support.com',
            first_seen: '2026-08-28T00:00:00Z',
            last_seen: '2026-08-30T14:23:10Z',
          },
          {
            id: 'NODE-DOMAIN-01',
            node_type: 'DOMAIN',
            canonical_value: 'paypa1-support.com',
            display_value: 'paypa1-support.com',
            first_seen: '2026-08-28T00:00:00Z',
            last_seen: '2026-08-30T14:23:10Z',
          },
          {
            id: 'NODE-IP-01',
            node_type: 'IP',
            canonical_value: '203.0.113.10',
            display_value: '203.0.113.10 (Observed Origin IP)',
            first_seen: '2026-08-25T00:00:00Z',
            last_seen: '2026-08-30T14:23:10Z',
          },
          {
            id: 'NODE-ASN-01',
            node_type: 'ASN',
            canonical_value: 'AS12345',
            display_value: 'AS12345 (Bulletproof Hosting Ltd)',
            first_seen: '2026-08-01T00:00:00Z',
            last_seen: '2026-08-30T14:23:10Z',
          },
          {
            id: 'NODE-URL-01',
            node_type: 'URL',
            canonical_value: 'http://verify-login.paypa1-support.com/auth',
            display_value: 'verify-login.paypa1-support.com',
            first_seen: '2026-08-30T14:23:10Z',
            last_seen: '2026-08-30T14:23:10Z',
          },
        ],
        edges: [
          {
            id: 'EDGE-01',
            source_node_id: `NODE-${emailId}`,
            target_node_id: 'NODE-SENDER-01',
            relationship_type: 'SENT_BY',
            relationship_origin: 'DIRECT',
            confidence: 99,
            strength: 'VERY_HIGH',
            evidence_reference: 'Header From: parsing',
          },
          {
            id: 'EDGE-02',
            source_node_id: 'NODE-SENDER-01',
            target_node_id: 'NODE-DOMAIN-01',
            relationship_type: 'RESOLVES_TO',
            relationship_origin: 'DIRECT',
            confidence: 98,
            strength: 'VERY_HIGH',
            evidence_reference: 'Domain extraction',
          },
          {
            id: 'EDGE-03',
            source_node_id: `NODE-${emailId}`,
            target_node_id: 'NODE-IP-01',
            relationship_type: 'PASSED_THROUGH',
            relationship_origin: 'DIRECT',
            confidence: 95,
            strength: 'HIGH',
            evidence_reference: 'Received header hop 1',
          },
          {
            id: 'EDGE-04',
            source_node_id: 'NODE-IP-01',
            target_node_id: 'NODE-ASN-01',
            relationship_type: 'BELONGS_TO_ASN',
            relationship_origin: 'DIRECT',
            confidence: 100,
            strength: 'VERY_HIGH',
            evidence_reference: 'BGP Routing Table Lookup',
          },
          {
            id: 'EDGE-05',
            source_node_id: `NODE-${emailId}`,
            target_node_id: 'NODE-URL-01',
            relationship_type: 'CONTAINS_URL',
            relationship_origin: 'DIRECT',
            confidence: 99,
            strength: 'VERY_HIGH',
            evidence_reference: 'HTML AST Parser',
          },
        ],
      } as unknown as T;
    }

    // Default single email detail
    return {
      id: emailId,
      subject: 'URGENT: Payroll Verification & Direct Deposit Update Required',
      sender: 'payroll-update@paypa1-support.com',
      sender_domain: 'paypa1-support.com',
      received_at: '2026-08-30T14:23:10Z',
      risk_score: 91,
      classification: 'PHISHING',
      status: 'UNDER_INVESTIGATION',
      message_id: '<202608301423.8801@paypa1-support.com>',
    } as unknown as T;
  }

  if (endpoint.startsWith('/campaigns')) {
    return [
      {
        id: 'CMP-2026-001',
        campaign_id: 'CMP-2026-001',
        confidence: 88,
        status: 'CANDIDATE',
        summary: 'Targeted Financial Phishing Campaign against HR & Payroll Departments',
        first_seen: '2026-08-28T10:00:00Z',
        last_seen: '2026-08-30T14:23:10Z',
        email_count: 3,
        clusters_count: 2,
        shared_indicators: ['203.0.113.10', 'paypa1-support.com', 'AS12345'],
        explanation: 'Three suspicious emails share identical origin infrastructure IP (203.0.113.10) and lookalike domain structure within a 48h temporal window.',
      },
      {
        id: 'CMP-2026-002',
        campaign_id: 'CMP-2026-002',
        confidence: 76,
        status: 'UNDER_REVIEW',
        summary: 'Executive Impersonation & Wire Fraud Cluster',
        first_seen: '2026-08-25T14:00:00Z',
        last_seen: '2026-08-30T12:10:00Z',
        email_count: 5,
        clusters_count: 1,
        shared_indicators: ['exec-management-corp.net', '198.51.100.89'],
        explanation: 'Multiple emails impersonating C-level executives utilizing common relay domain with spoofed Reply-To headers.',
      },
    ] as unknown as T;
  }

  if (endpoint.startsWith('/cases')) {
    return [
      {
        id: 'CASE-2026-0042',
        case_id: 'CASE-2026-0042',
        title: 'High-Risk Financial Credential Harvesting Campaign',
        priority: 'HIGH',
        status: 'OPEN',
        created_at: '2026-08-30T14:30:00Z',
        assigned_to: 'Senior Analyst Jayant',
        related_emails_count: 3,
        campaigns_count: 1,
        infrastructure_clusters_count: 2,
        summary: 'Active credential harvesting campaign attempting to compromise HR payroll accounts.',
      },
      {
        id: 'CASE-2026-0039',
        case_id: 'CASE-2026-0039',
        title: 'Executive Wire Transfer BEC Attempt',
        priority: 'CRITICAL',
        status: 'UNDER_REVIEW',
        created_at: '2026-08-29T09:15:00Z',
        assigned_to: 'SOC Lead Alex',
        related_emails_count: 5,
        campaigns_count: 1,
        infrastructure_clusters_count: 1,
        summary: 'Spoofed CEO wire authorization request sent to finance team.',
      },
    ] as unknown as T;
  }

  return {} as T;
}

export const api = {
  getMetrics: () => fetcher<{ threats_detected: number; high_risk: number; open_cases: number; campaign_candidates: number; infrastructure_clusters: number }>('/metrics'),
  getEmails: () => fetcher<EmailSummary[]>('/emails'),
  getEmailDetail: (id: string) => fetcher<EmailSummary>(`/emails/${id}`),
  getEmailThreatAssessment: (id: string) => fetcher<ThreatAssessment>(`/emails/${id}/threat`),
  getEmailForensics: (id: string) => fetcher<HeaderForensics>(`/emails/${id}/forensics`),
  getEmailGraph: (id: string) => fetcher<InvestigationGraph>(`/emails/${id}/graph`),
  getCampaigns: () => fetcher<CampaignCandidate[]>('/campaigns'),
  getCases: () => fetcher<Case[]>('/cases'),
  
  updateCampaignStatus: async (campaignId: string, status: string) => {
    console.log(`Updating campaign ${campaignId} status to ${status}`);
    return { success: true, campaignId, status };
  },
  
  updateCaseStatus: async (caseId: string, status: string) => {
    console.log(`Updating case ${caseId} status to ${status}`);
    return { success: true, caseId, status };
  },

  addAnalystNote: async (entityType: string, entityId: string, content: string) => {
    console.log(`Adding note to ${entityType}:${entityId}`, content);
    return {
      id: `NOTE-${Date.now()}`,
      author: 'Current Analyst',
      timestamp: new Date().toISOString(),
      content,
      entity_type: entityType,
      entity_id: entityId,
    };
  },
};
