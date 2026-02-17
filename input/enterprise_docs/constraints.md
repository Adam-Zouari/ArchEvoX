# Constraints & Requirements

## Regulatory / Compliance
- GDPR compliance required (EU customers represent 30% of user base)
- CCPA compliance required (California users)
- SOC 2 Type II certification maintained
- PII must be encrypted at rest and in transit
- Data residency: EU data must stay in eu-west-1, US data in us-east-1

## Budget
- Current annual data infrastructure spend: $800K
- Maximum acceptable increase: 30% ($1.04M total)
- Preference for usage-based pricing over large upfront commitments

## SLAs
- Dashboard refresh: < 1 hour for executive dashboards, < 15 min for operational
- API response time: p95 < 200ms for data API endpoints
- Pipeline failure recovery: < 2 hours for critical pipelines
- Data freshness: < 5 minutes for real-time streams, < 1 hour for batch

## Security
- All data access must go through centralized authentication (Okta SSO)
- Role-based access control (RBAC) on all data assets
- Audit logging for all data access and modifications
- No direct production database access for analytics queries

## Technical
- Must support multi-cloud (primary AWS, secondary GCP for specific workloads)
- Kubernetes-native deployments preferred
- Infrastructure as Code (Terraform) for all new infrastructure
- Zero-downtime deployments required
