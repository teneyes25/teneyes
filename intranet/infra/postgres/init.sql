create extension if not exists pgcrypto;

create table if not exists module_items (
  id uuid primary key default gen_random_uuid(),
  module_key text not null,
  title text not null,
  body text not null default '',
  tags text[] not null default '{}',
  status text not null default 'published',
  author_id text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists module_items_module_idx on module_items (module_key, updated_at desc);
create index if not exists module_items_tags_idx on module_items using gin (tags);

create table if not exists approvals (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  body text not null,
  requester_id text not null,
  approver_id text not null,
  status text not null check (status in ('pending', 'approved', 'rejected')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists document_folders (
  id uuid primary key default gen_random_uuid(),
  parent_id uuid references document_folders(id),
  name text not null,
  allowed_roles text[] not null default '{employee}',
  created_at timestamptz not null default now()
);

create table if not exists documents (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  file_name text not null,
  object_key text not null unique,
  content_type text not null,
  size_bytes bigint not null,
  tags text[] not null default '{}',
  folder_id uuid references document_folders(id),
  allowed_roles text[] not null default '{employee}',
  created_by text,
  created_at timestamptz not null default now()
);

create index if not exists documents_title_idx on documents using gin (to_tsvector('simple', title));
create index if not exists documents_tags_idx on documents using gin (tags);
create index if not exists documents_roles_idx on documents using gin (allowed_roles);

create table if not exists attendance_events (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  event_type text not null check (event_type in ('clock_in', 'clock_out')),
  event_at timestamptz not null default now(),
  memo text
);

create index if not exists attendance_user_time_idx on attendance_events (user_id, event_at desc);

create table if not exists leave_balances (
  user_id text not null,
  year int not null,
  annual_total numeric(5, 2) not null default 15,
  annual_used numeric(5, 2) not null default 0,
  primary key (user_id, year)
);

create table if not exists audit_logs (
  id uuid primary key default gen_random_uuid(),
  actor_id text not null,
  actor_email text not null,
  action text not null,
  target_type text not null,
  target_id text,
  ip_address text,
  user_agent text,
  metadata jsonb not null default '{}',
  created_at timestamptz not null default now()
);

create index if not exists audit_logs_action_idx on audit_logs (action, created_at desc);
create index if not exists audit_logs_actor_idx on audit_logs (actor_id, created_at desc);

create table if not exists agent_settings (
  key text primary key,
  value text not null,
  updated_at timestamptz not null default now()
);

create table if not exists agent_conversations (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  title text,
  expires_at timestamptz not null default now() + interval '3 days',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists agent_messages (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid not null references agent_conversations(id) on delete cascade,
  role text not null check (role in ('user', 'assistant')),
  content text not null,
  metadata jsonb not null default '{}',
  created_at timestamptz not null default now()
);

create table if not exists agent_knowledge (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  content text not null,
  source_type text not null,
  tags text[] not null default '{}',
  metadata jsonb not null default '{}',
  created_by text not null,
  created_at timestamptz not null default now()
);

create index if not exists agent_conversations_user_idx on agent_conversations (user_id, updated_at desc);
create index if not exists agent_messages_conversation_idx on agent_messages (conversation_id, created_at asc);
create index if not exists agent_knowledge_tags_idx on agent_knowledge using gin (tags);
create index if not exists agent_knowledge_text_idx on agent_knowledge using gin (to_tsvector('simple', title || ' ' || content));

insert into document_folders (name, allowed_roles)
values ('전사 공유', '{employee}'), ('대리점 자료', '{dealer,sales,admin}')
on conflict do nothing;
