# Connect - Memory-Efficient Database Schema

**Goal**: Support 5000 users with < 512MB RAM usage

## Memory Optimization Strategies

1. **Efficient Data Types**: Use smallest appropriate types
2. **Indexed Columns**: Only index frequently queried columns
3. **Partitioning**: Partition large tables by workspace
4. **Denormalization**: Strategic denormalization for read-heavy operations
5. **Caching**: Redis for frequently accessed data
6. **Lazy Loading**: Load permissions/roles on-demand
7. **Bitmap Permissions**: Use bitmasks for RBAC/ABAC

## Core Tables

### users
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    avatar_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = TRUE;
```

**Memory**: ~200 bytes/user × 5000 = ~1MB

### workspaces
```sql
CREATE TABLE workspaces (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    owner_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    settings JSONB DEFAULT '{}'::jsonb,
    member_limit INTEGER DEFAULT 10,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_workspaces_slug ON workspaces(slug);
CREATE INDEX idx_workspaces_owner ON workspaces(owner_id);
```

**Memory**: ~300 bytes/workspace × 100 = ~30KB

### workspace_members
```sql
CREATE TABLE workspace_members (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role_id SMALLINT NOT NULL, -- Bitmap: 0=Owner, 1=Admin, 2=Member, 3=Viewer, 4=Guest
    permissions BIGINT DEFAULT 0, -- Bitmap for ABAC (64 permissions max)
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(workspace_id, user_id)
);

CREATE INDEX idx_wm_workspace ON workspace_members(workspace_id);
CREATE INDEX idx_wm_user ON workspace_members(user_id);
CREATE INDEX idx_wm_role ON workspace_members(role_id);
```

**Memory**: ~50 bytes/member × 10,000 = ~500KB

## Permission System (RBAC/ABAC with Bitmasks)

### Predefined Roles (role_id as bitmask)
```
0 = OWNER       (all permissions)
1 = ADMIN       (manage users, projects, settings)
2 = MEMBER      (create issues, docs, participate)
3 = VIEWER      (read-only access)
4 = GUEST       (limited project access)
```

### Permission Bits (64-bit bitmask)
```
Bit 0:  CREATE_PROJECT
Bit 1:  EDIT_PROJECT
Bit 2:  DELETE_PROJECT
Bit 3:  CREATE_ISSUE
Bit 4:  EDIT_ISSUE
Bit 5:  DELETE_ISSUE
Bit 6:  MANAGE_USERS
Bit 7:  MANAGE_ROLES
Bit 8:  CREATE_DOCUMENT
Bit 9:  EDIT_DOCUMENT
Bit 10: DELETE_DOCUMENT
Bit 11: SEND_MESSAGE
Bit 12: DELETE_MESSAGE
Bit 13: CREATE_CHANNEL
Bit 14: MANAGE_CHANNEL
Bit 15: START_VIDEO_CALL
Bit 16: RECORD_MEETING
Bit 17: MANAGE_INTEGRATIONS
Bit 18: VIEW_ANALYTICS
Bit 19: EXPORT_DATA
Bit 20: MANAGE_BILLING
Bit 21-63: Reserved for future use
```

### Permission Check (in application code)
```python
def has_permission(user_permissions: int, permission: str) -> bool:
    """Check if user has specific permission using bitwise AND"""
    permission_bits = {
        'CREATE_PROJECT': 1 << 0,
        'EDIT_PROJECT': 1 << 1,
        'DELETE_PROJECT': 1 << 2,
        # ... etc
    }
    return bool(user_permissions & permission_bits[permission])
```

**Memory**: 8 bytes per user for permissions (already in workspace_members)

## Projects & Issues

### projects
```sql
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER REFERENCES workspaces(id) ON DELETE CASCADE,
    key VARCHAR(10) NOT NULL, -- e.g., "PROJ"
    name VARCHAR(100) NOT NULL,
    description TEXT,
    owner_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_archived BOOLEAN DEFAULT FALSE,
    UNIQUE(workspace_id, key)
);

CREATE INDEX idx_projects_workspace ON projects(workspace_id);
CREATE INDEX idx_projects_key ON projects(workspace_id, key);
```

**Memory**: ~250 bytes/project × 500 = ~125KB

### issues
```sql
CREATE TABLE issues (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    issue_number INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status SMALLINT DEFAULT 0, -- 0=Backlog, 1=Todo, 2=InProgress, 3=InReview, 4=Done
    priority SMALLINT DEFAULT 2, -- 0=Urgent, 1=High, 2=Medium, 3=Low
    assignee_id INTEGER REFERENCES users(id),
    reporter_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date DATE,
    estimate INTEGER, -- in minutes
    UNIQUE(project_id, issue_number)
);

CREATE INDEX idx_issues_project ON issues(project_id);
CREATE INDEX idx_issues_assignee ON issues(assignee_id);
CREATE INDEX idx_issues_status ON issues(status);
CREATE INDEX idx_issues_number ON issues(project_id, issue_number);
```

**Memory**: ~300 bytes/issue × 10,000 = ~3MB

### issue_labels
```sql
CREATE TABLE labels (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER REFERENCES workspaces(id) ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL,
    color VARCHAR(7) NOT NULL, -- Hex color
    UNIQUE(workspace_id, name)
);

CREATE TABLE issue_labels (
    issue_id INTEGER REFERENCES issues(id) ON DELETE CASCADE,
    label_id INTEGER REFERENCES labels(id) ON DELETE CASCADE,
    PRIMARY KEY (issue_id, label_id)
);
```

**Memory**: ~100KB total

### issue_comments
```sql
CREATE TABLE issue_comments (
    id SERIAL PRIMARY KEY,
    issue_id INTEGER REFERENCES issues(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_edited BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_comments_issue ON issue_comments(issue_id);
```

**Memory**: ~200 bytes/comment × 20,000 = ~4MB

## Messaging

### channels
```sql
CREATE TABLE channels (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER REFERENCES workspaces(id) ON DELETE CASCADE,
    name VARCHAR(80) NOT NULL,
    description TEXT,
    is_private BOOLEAN DEFAULT FALSE,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(workspace_id, name)
);

CREATE INDEX idx_channels_workspace ON channels(workspace_id);
```

**Memory**: ~200 bytes/channel × 200 = ~40KB

### messages
```sql
CREATE TABLE messages (
    id BIGSERIAL PRIMARY KEY,
    channel_id INTEGER REFERENCES channels(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_edited BOOLEAN DEFAULT FALSE,
    parent_id BIGINT REFERENCES messages(id) -- for threading
);

CREATE INDEX idx_messages_channel ON messages(channel_id, created_at DESC);
CREATE INDEX idx_messages_thread ON messages(parent_id) WHERE parent_id IS NOT NULL;
```

**Memory**: ~250 bytes/message × 100,000 = ~25MB
**Note**: Archive messages older than 90 days to external storage

### message_reactions
```sql
CREATE TABLE message_reactions (
    message_id BIGINT REFERENCES messages(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    emoji VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (message_id, user_id, emoji)
);
```

**Memory**: ~30 bytes/reaction × 50,000 = ~1.5MB

## Documents

### documents
```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER REFERENCES workspaces(id) ON DELETE CASCADE,
    parent_id INTEGER REFERENCES documents(id), -- for folders
    name VARCHAR(255) NOT NULL,
    doc_type SMALLINT DEFAULT 0, -- 0=folder, 1=doc, 2=spreadsheet, 3=presentation
    content_url VARCHAR(500), -- S3 path for large content
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_docs_workspace ON documents(workspace_id);
CREATE INDEX idx_docs_parent ON documents(parent_id);
```

**Memory**: ~200 bytes/document × 5,000 = ~1MB
**Note**: Store actual content in S3, not in database

## Activity & Audit

### activity_logs
```sql
CREATE TABLE activity_logs (
    id BIGSERIAL PRIMARY KEY,
    workspace_id INTEGER REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),
    action SMALLINT NOT NULL, -- 0=created, 1=updated, 2=deleted, etc.
    entity_type SMALLINT NOT NULL, -- 0=issue, 1=project, 2=doc, etc.
    entity_id INTEGER NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (created_at);

-- Partition by month for efficient archival
CREATE TABLE activity_logs_2024_01 PARTITION OF activity_logs
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE INDEX idx_activity_workspace ON activity_logs(workspace_id, created_at DESC);
```

**Memory**: ~150 bytes/log × 50,000 = ~7.5MB
**Note**: Archive logs older than 6 months

## Calendar & Events

### events
```sql
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER REFERENCES workspaces(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_all_day BOOLEAN DEFAULT FALSE,
    recurrence_rule VARCHAR(200) -- RRULE format
);

CREATE INDEX idx_events_workspace ON events(workspace_id, start_time);
```

**Memory**: ~250 bytes/event × 2,000 = ~500KB

## Memory Calculation (5000 users, 100 workspaces)

| Table               | Memory Estimate |
|---------------------|-----------------|
| users               | 1 MB            |
| workspaces          | 30 KB           |
| workspace_members   | 500 KB          |
| projects            | 125 KB          |
| issues              | 3 MB            |
| labels              | 100 KB          |
| issue_comments      | 4 MB            |
| channels            | 40 KB           |
| messages            | 25 MB           |
| message_reactions   | 1.5 MB          |
| documents           | 1 MB            |
| activity_logs       | 7.5 MB          |
| events              | 500 KB          |
| **TOTAL**           | **~44 MB**      |

### Additional Overhead

- PostgreSQL shared buffers: 128 MB
- PostgreSQL work mem: 4MB × 50 connections = 200 MB
- OS cache: 50 MB
- Application (Django): 50 MB
- Redis cache: 30 MB

**Total RAM Usage**: ~502 MB < 512 MB ✓

## Optimization Techniques

### 1. Connection Pooling
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'CONN_MAX_AGE': 600,  # Reuse connections
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000'
        }
    }
}
```

### 2. Query Optimization
- Use `select_related()` and `prefetch_related()`
- Avoid N+1 queries
- Use `only()` and `defer()` for large models

### 3. Caching Strategy
```python
# Cache user permissions for 5 minutes
@cache_memoize(timeout=300, args_rewrite=lambda u: u.id)
def get_user_permissions(user):
    return user.workspace_members.values_list('permissions', flat=True)
```

### 4. Database Settings (postgresql.conf)
```conf
shared_buffers = 128MB
effective_cache_size = 256MB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
work_mem = 4MB
min_wal_size = 1GB
max_wal_size = 4GB
```

## Indexing Strategy

**Rules**:
1. Index foreign keys used in JOINs
2. Index columns used in WHERE clauses frequently
3. Use partial indexes for filtered queries
4. Use composite indexes for multi-column queries
5. Avoid over-indexing (max 5 indexes per table)

## Partitioning Strategy

**Large Tables** (> 100K rows):
- `messages`: Partition by channel_id and date
- `activity_logs`: Partition by date (monthly)
- `documents`: Partition by workspace_id

## Archival Strategy

**Data Retention**:
- Messages: 90 days (then archive to S3)
- Activity logs: 6 months (then archive)
- Deleted entities: 30 days (then hard delete)

## Monitoring

**Key Metrics**:
- Database size: `SELECT pg_size_pretty(pg_database_size('connect'));`
- Table sizes: `SELECT pg_size_pretty(pg_total_relation_size('table_name'));`
- Index usage: `pg_stat_user_indexes`
- Connection count: `SELECT count(*) FROM pg_stat_activity;`
- Cache hit ratio: `SELECT sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) FROM pg_statio_user_tables;`

Target: Cache hit ratio > 99%
