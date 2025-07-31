# Supabase Configuration for Task Manager

## Database Schema

The task manager requires the following database tables in Supabase:

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Tasks Table
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    priority VARCHAR(10) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),
    status VARCHAR(10) DEFAULT 'pending' CHECK (status IN ('pending', 'completed')),
    due_date TIMESTAMP WITH TIME ZONE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);
```

## Row Level Security (RLS)

Enable RLS on both tables and create policies:

### Users Table Policies
```sql
-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Users can only see their own profile
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = id);
```

### Tasks Table Policies
```sql
-- Enable RLS
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;

-- Users can only see their own tasks
CREATE POLICY "Users can view own tasks" ON tasks
    FOR SELECT USING (auth.uid() = user_id);

-- Users can insert their own tasks
CREATE POLICY "Users can insert own tasks" ON tasks
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Users can update their own tasks
CREATE POLICY "Users can update own tasks" ON tasks
    FOR UPDATE USING (auth.uid() = user_id);

-- Users can delete their own tasks
CREATE POLICY "Users can delete own tasks" ON tasks
    FOR DELETE USING (auth.uid() = user_id);
```

## Indexes for Performance

```sql
-- Index on user_id for tasks table
CREATE INDEX idx_tasks_user_id ON tasks(user_id);

-- Index on status for filtering
CREATE INDEX idx_tasks_status ON tasks(status);

-- Index on priority for filtering
CREATE INDEX idx_tasks_priority ON tasks(priority);

-- Index on due_date for filtering
CREATE INDEX idx_tasks_due_date ON tasks(due_date);

-- Index on created_at for ordering
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);

-- Composite index for common queries
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);
```

## Authentication Setup

1. Enable Email authentication in Supabase Auth settings
2. Configure email templates if needed
3. Set up redirect URLs for email confirmation

## Environment Variables Required

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon/public key
- `JWT_SECRET_KEY`: Secret key for JWT token signing

## API Integration

The backend uses Supabase client for:
- User authentication (sign up, sign in)
- Database operations (CRUD for tasks)
- Row Level Security for data isolation

All database operations are performed through the DatabaseService class which handles Supabase client interactions.
