# ZK Caller Verification System - Architecture

## Overview

The ZK Caller Verification System is a secure, privacy-preserving application for authenticating call center agents using blockchain-based identities and zero-knowledge proofs. This document outlines the system architecture, components, data flow, and security model.

## System Architecture

The application follows a modular, layered architecture with clear separation of concerns:

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│      UI Layer       │     │      API Layer      │     │   Blockchain Layer  │
│  (Streamlit + Web)  │────▶│   (FastAPI + REST)  │────▶│   (Aleo Network)    │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
           │                          │                           │
           │                          │                           │
           ▼                          ▼                           ▼
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│   Business Logic    │     │    Data Access      │     │   Security Layer    │
│   (Core Services)   │────▶│ (SQLAlchemy + ORM)  │────▶│  (Auth + Crypto)    │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
                                      │
                                      │
                                      ▼
                            ┌─────────────────────┐
                            │     Database        │
                            │ (PostgreSQL/SQLite) │
                            └─────────────────────┘
```

## Components

### 1. UI Layer

- **Streamlit Application**: Provides interfaces for:

  - HR Admin: Enable employees as agents
  - Agent Dashboard: Generate verification codes
  - Agent Management: Revoke/reactivate agents and view logs

- **Web Interface**: (Planned) A responsive web application for wider access

### 2. API Layer

- **FastAPI Framework**: High-performance REST API with:

  - Automatic OpenAPI documentation
  - Request validation with Pydantic models
  - Dependency injection for services
  - Authentication middleware

- **Endpoints**:
  - `/auth`: Authentication and token management
  - `/employees`: Employee CRUD operations
  - `/agents`: Agent enablement and management
  - `/verify`: Verification code generation and validation

### 3. Business Logic

- **Core Services**:
  - Employee management
  - Agent identity management
  - OTP generation and validation
  - Audit logging

### 4. Data Access Layer

- **ORM**: SQLAlchemy for database abstraction with:

  - Model definitions
  - Query building
  - Transaction management

- **Repositories**: Data access patterns for:
  - Employees
  - Agents/Blockchain identities
  - Users
  - Audit logs

### 5. Security Layer

- **Authentication**: JWT-based authentication
- **Cryptography**: Secure key management and encryption for sensitive data
- **RBAC**: Role-based access controls (admin, hr_manager, hr_staff, agent)
- **Row-Level Security**: PostgreSQL RLS for database-level access control

### 6. Blockchain Layer

- **Aleo Integration**: Zero-knowledge proofs for agent verification
- **Mock Blockchain**: Development-friendly simulation mode

### 7. Database

- **PostgreSQL**: Production database with RLS
- **SQLite**: Development and testing database

## Data Flow

### Agent Enablement Flow

1. HR Admin selects an employee to enable as agent
2. System generates cryptographic seed for OTP
3. System calls Aleo network to mint a badge with employee identity
4. Badge and blockchain identity are stored in the database
5. Agent is now enabled to generate verification codes

### Verification Code Generation Flow

1. Agent selects their identity in the dashboard
2. Agent requests a verification code
3. System retrieves agent's seed and blockchain identity
4. System generates a time-based OTP using the seed
5. OTP is displayed to the agent for sharing with customer
6. Code automatically expires after the time window

### Authentication Flow

1. User submits credentials
2. System validates credentials against database
3. If valid, JWT token is generated with user's role and permissions
4. Token is used for subsequent API calls
5. Token expiration enforces re-authentication

## Security Model

### Data Protection

- **Encryption at Rest**: Sensitive data (private keys, seeds) are encrypted
- **Secure APIs**: Authentication and authorization for all endpoints
- **Row-Level Security**: PostgreSQL RLS restricts data access based on user role and context

### Zero-Knowledge Proofs

- **Privacy-Preserving**: Verification occurs without revealing the underlying secrets
- **Timing-Based Security**: OTPs valid only for short time windows
- **Tamper-Resistant**: Blockchain-based identity management

### Audit and Compliance

- **Comprehensive Logging**: All security-relevant actions are logged
- **Non-Repudiation**: Blockchain provides cryptographic proof of agent identity
- **Traceability**: All actions can be traced to specific users and timestamps

## Database Schema

### Core Tables

- **employees**: Employee identity records
- **blockchain_identities**: Blockchain identities for agents
- **users**: User accounts for system access
- **audit_logs**: Comprehensive audit trail
- **auth_attempts**: Authentication attempt tracking

### Key Relationships

- One employee can have at most one blockchain identity
- Users can be linked to employees (for agent users)
- Audit logs reference users and resources

## Configuration and Environment

- **Environment Variables**: All configuration through environment variables
- **Settings Management**: Centralized with validation
- **Development Mode**: Simplified setup for development
- **Production Mode**: Enhanced security requirements enforced

## Future Extensions

- **Web Interface**: Responsive web UI beyond Streamlit
- **Multi-Factor Authentication**: Additional security for admin users
- **Delegation**: Temporary agent delegation with secure handoff
- **Analytics Dashboard**: Security monitoring and trend analysis
- **External Identity Integration**: Single sign-on capabilities
