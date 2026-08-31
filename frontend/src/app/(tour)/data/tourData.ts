export const tourData = {
  incident: {
    from: 'billing@paypa1-support.com',
    subject: 'Urgent Payment Verification Required',
    date: '2026-09-01T08:14:22Z',
    body: 'Your account requires immediate verification due to unusual activity. Please click the button below to verify your payment details.\n\n[ VERIFY ACCOUNT ]\n\nIf you do not verify within 24 hours, your account will be suspended.',
    url: 'https://paypa1-support.com/verify?token=8f92a',
    size: '84 KB'
  },
  detection: {
    riskScore: 91,
    classification: 'PHISHING',
    confidence: 'HIGH',
    signals: [
      { id: 'S1', label: 'LOOKALIKE DOMAIN', evidence: 'paypa1-support.com' },
      { id: 'S2', label: 'SPF FAILURE', evidence: 'SoftFail' },
      { id: 'S3', label: 'DKIM FAILURE', evidence: 'Signature Invalid' },
      { id: 'S4', label: 'DMARC FAILURE', evidence: 'Reject Policy Failed' },
      { id: 'S5', label: 'SUSPICIOUS URL', evidence: 'Newly Registered Domain' },
      { id: 'S6', label: 'SOCIAL ENGINEERING', evidence: 'Urgency & Account Suspension Threat' }
    ]
  },
  headers: {
    raw: `Received: from mail.paypa1-support.com (203.0.113.42)
  by mx.victim-corp.com with ESMTPS id 12345
  for <finance@victim-corp.com>;
  Tue, 01 Sep 2026 08:14:22 +0000
From: "Billing Support" <billing@paypa1-support.com>
To: finance@victim-corp.com
Subject: Urgent Payment Verification Required
Message-ID: <987654321@paypa1-support.com>
Authentication-Results: mx.victim-corp.com;
  spf=softfail (domain of transitioning paypa1-support.com does not designate 203.0.113.42 as permitted sender);
  dkim=fail (bad signature) header.d=paypa1-support.com;
  dmarc=fail (p=none sp=none dis=none) header.from=paypa1-support.com
Date: Tue, 01 Sep 2026 08:14:20 +0000`,
    parsed: [
      { key: 'SPF', result: 'FAILED', detail: 'IP 203.0.113.42 not permitted' },
      { key: 'DKIM', result: 'FAILED', detail: 'Signature mismatch' },
      { key: 'DMARC', result: 'FAILED', detail: 'Alignment failure' }
    ]
  },
  relay: {
    hops: [
      { step: 1, label: 'SENDER', detail: 'mail.paypa1-support.com' },
      { step: 2, label: 'MAIL SERVER', detail: 'SMTP Relay' },
      { step: 3, label: 'IP ADDRESS', detail: '203.0.113.42' },
      { step: 4, label: 'DESTINATION', detail: 'mx.victim-corp.com' }
    ],
    infrastructure: {
      ip: '203.0.113.42',
      asn: 'AS64496',
      network: 'Example Hosting Provider',
      geolocation: 'Region-3',
      confidence: 'MEDIUM'
    }
  },
  graph: {
    nodes: [
      { id: 'email1', label: 'EMAIL', type: 'email' },
      { id: 'domain', label: 'paypa1-support.com', type: 'domain' },
      { id: 'ip', label: '203.0.113.42', type: 'ip' },
      { id: 'asn', label: 'AS64496', type: 'asn' },
      { id: 'email2', label: 'EMAIL (Related)', type: 'email' },
      { id: 'email3', label: 'EMAIL (Related)', type: 'email' },
      { id: 'campaign', label: 'CAMPAIGN CANDIDATE', type: 'campaign' }
    ]
  },
  case: {
    id: 'CASE-2026-0042',
    evidenceItems: [
      'Original Email',
      'Header Analysis',
      'Authentication Results',
      'Relay Chain',
      'IP Intelligence',
      'Domain Intelligence',
      'Related Emails',
      'Investigation Graph',
      'Analyst Notes',
      'Analyst Verdict'
    ]
  }
};
