#!/usr/bin/env python3
"""
Phase 3 Security & Compliance Database Migration
Creates audit trail, security event, and data privacy tables.
"""

import os
import sys
from datetime import datetime

def create_phase3_tables():
    """Create Phase 3 security and compliance tables"""
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("DATABASE_URL not found")
        return False
    
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            print("🔐 Starting Phase 3 Security & Compliance migration...")
            
            # Create audit_log table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES "user"(id) ON DELETE SET NULL,
                    action_type VARCHAR(50) NOT NULL,
                    resource_type VARCHAR(50) NOT NULL,
                    resource_id INTEGER,
                    details JSONB,
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    session_id VARCHAR(255),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    organization_id INTEGER REFERENCES organization(id) ON DELETE SET NULL
                );
            """))
            print("✅ Created audit_log table")
            
            # Create indexes for audit_log
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id);
                CREATE INDEX IF NOT EXISTS idx_audit_log_action_type ON audit_log(action_type);
                CREATE INDEX IF NOT EXISTS idx_audit_log_resource_type ON audit_log(resource_type);
                CREATE INDEX IF NOT EXISTS idx_audit_log_resource_id ON audit_log(resource_id);
                CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp);
                CREATE INDEX IF NOT EXISTS idx_audit_log_ip_address ON audit_log(ip_address);
                CREATE INDEX IF NOT EXISTS idx_audit_log_organization_id ON audit_log(organization_id);
            """))
            print("✅ Created audit_log indexes")
            
            # Create security_event table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS security_event (
                    id SERIAL PRIMARY KEY,
                    event_type VARCHAR(50) NOT NULL,
                    severity VARCHAR(20) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
                    source_ip VARCHAR(45),
                    user_id INTEGER REFERENCES "user"(id) ON DELETE SET NULL,
                    details JSONB,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolved_by INTEGER REFERENCES "user"(id) ON DELETE SET NULL,
                    resolved_at TIMESTAMP,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            print("✅ Created security_event table")
            
            # Create indexes for security_event
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_security_event_type ON security_event(event_type);
                CREATE INDEX IF NOT EXISTS idx_security_event_severity ON security_event(severity);
                CREATE INDEX IF NOT EXISTS idx_security_event_source_ip ON security_event(source_ip);
                CREATE INDEX IF NOT EXISTS idx_security_event_resolved ON security_event(resolved);
                CREATE INDEX IF NOT EXISTS idx_security_event_timestamp ON security_event(timestamp);
                CREATE INDEX IF NOT EXISTS idx_security_event_user_id ON security_event(user_id);
            """))
            print("✅ Created security_event indexes")
            
            # Create data_privacy_request table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS data_privacy_request (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
                    request_type VARCHAR(20) NOT NULL CHECK (request_type IN ('export', 'delete', 'modify')),
                    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
                    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    file_path VARCHAR(255),
                    processed_by INTEGER REFERENCES "user"(id) ON DELETE SET NULL,
                    notes TEXT
                );
            """))
            print("✅ Created data_privacy_request table")
            
            # Create indexes for data_privacy_request
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_privacy_request_user_id ON data_privacy_request(user_id);
                CREATE INDEX IF NOT EXISTS idx_privacy_request_type ON data_privacy_request(request_type);
                CREATE INDEX IF NOT EXISTS idx_privacy_request_status ON data_privacy_request(status);
                CREATE INDEX IF NOT EXISTS idx_privacy_request_requested_at ON data_privacy_request(requested_at);
            """))
            print("✅ Created data_privacy_request indexes")
            
            # Create user_session table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS user_session (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
                    session_token VARCHAR(255) NOT NULL UNIQUE,
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    device_fingerprint VARCHAR(255),
                    location_info JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    logout_reason VARCHAR(50)
                );
            """))
            print("✅ Created user_session table")
            
            # Create indexes for user_session
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_user_session_user_id ON user_session(user_id);
                CREATE INDEX IF NOT EXISTS idx_user_session_token ON user_session(session_token);
                CREATE INDEX IF NOT EXISTS idx_user_session_active ON user_session(is_active);
                CREATE INDEX IF NOT EXISTS idx_user_session_last_activity ON user_session(last_activity);
            """))
            print("✅ Created user_session indexes")
            
            # Create security_policy table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS security_policy (
                    id SERIAL PRIMARY KEY,
                    organization_id INTEGER REFERENCES organization(id) ON DELETE CASCADE,
                    policy_name VARCHAR(100) NOT NULL,
                    policy_type VARCHAR(50) NOT NULL CHECK (policy_type IN ('password', 'session', 'access', 'data_retention')),
                    policy_config JSONB NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER REFERENCES "user"(id) ON DELETE SET NULL
                );
            """))
            print("✅ Created security_policy table")
            
            # Create indexes for security_policy
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_security_policy_org_id ON security_policy(organization_id);
                CREATE INDEX IF NOT EXISTS idx_security_policy_type ON security_policy(policy_type);
                CREATE INDEX IF NOT EXISTS idx_security_policy_active ON security_policy(is_active);
            """))
            print("✅ Created security_policy indexes")
            
            # Create initial audit log entry for this migration
            conn.execute(text("""
                INSERT INTO audit_log (
                    action_type, 
                    resource_type, 
                    details, 
                    ip_address, 
                    user_agent,
                    timestamp
                ) VALUES (
                    'create', 
                    'database_migration', 
                    '{"migration": "phase3_security_compliance", "tables_created": ["audit_log", "security_event", "data_privacy_request", "user_session", "security_policy"]}',
                    '127.0.0.1',
                    'Phase3MigrationScript/1.0',
                    CURRENT_TIMESTAMP
                );
            """))
            print("✅ Created initial audit log entry")
            
            conn.commit()
            print("🎉 Phase 3 Security & Compliance migration completed successfully!")
            
            # Display table summary
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('audit_log', 'security_event', 'data_privacy_request', 'user_session', 'security_policy')
                ORDER BY table_name;
            """))
            
            tables = [row[0] for row in result.fetchall()]
            print(f"\n📊 Created tables: {', '.join(tables)}")
            
            return True
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def main():
    """Main migration function"""
    print("🔐 Phase 3 Security & Compliance Database Migration")
    print("=" * 60)
    
    # Check if running in production
    environment = os.getenv('ENVIRONMENT', 'development')
    print(f"Environment: {environment}")
    
    if environment == 'production':
        print("⚠️  Running in PRODUCTION mode")
        # In production, we might want additional confirmations
    
    # Run migration
    success = create_phase3_tables()
    
    if success:
        print("\n✅ Phase 3 migration completed successfully!")
        print("🔐 Security and compliance features are now available")
        print("\nNew capabilities:")
        print("  • Comprehensive audit trails")
        print("  • Security event monitoring")
        print("  • Data privacy request handling")
        print("  • Session management")
        print("  • Security policy configuration")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
