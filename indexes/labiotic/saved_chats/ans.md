# Q: 

**Overview**

remedi‑lab is a full‑stack platform designed to enable collaborative scientific research.  
On the client side it ships a Vite‑powered React + TypeScript application that provides a rich UI for working in laboratories, drawing on shared whiteboards, chatting, managing tasks, and generating research reports.  The app is split into reusable hooks (see `hooks/`), a supabase integration helper (`lib/supabase.ts`), and type declarations (`types/`) that describe the API payloads used across the code base.

On the server side it uses Supabase as a Postgres database‑as‑a‑service.  The migrations in `supabase/migrations/` create the core tables that power the platform:

```sql
-- 20250607124954_frosty_meadow.sql
CREATE TABLE users (
  id uuid PRIMARY KEY,
  email text UNIQUE NOT NULL,
  username text,
  avatar_url text
);

CREATE TABLE labs (
  id uuid PRIMARY KEY,
  name text NOT NULL,
  owner_id uuid REFERENCES users(id)
);

CREATE TABLE lab_members (
  lab_id uuid REFERENCES labs(id),
  user_id uuid REFERENCES users(id),
  role text NOT NULL,
  PRIMARY KEY (lab_id, user_id)
);

CREATE TABLE whiteboards (
  id uuid PRIMARY KEY,
  lab_id uuid REFERENCES labs(id),
  name text NOT NULL
);

CREATE TABLE reports (
  id uuid PRIMARY KEY,
  lab_id uuid REFERENCES labs(id),
  title text,
  content jsonb
);

CREATE TABLE compounds (
  id uuid PRIMARY KEY,
  smiles text NOT NULL,
  name text
);

CREATE TABLE proteins (
  id uuid PRIMARY KEY,
  pdb_id text NOT NULL,
  name text
);

CREATE TABLE chat_messages (
  id uuid PRIMARY KEY,
  lab_id uuid REFERENCES labs(id),
  user_id uuid REFERENCES users(id),
  message text,
  created_at timestamp with time zone DEFAULT now()
);

CREATE TABLE todos (
  id uuid PRIMARY KEY,
  lab_id uuid REFERENCES labs(id),
  task text,
  done boolean DEFAULT false
);
```

Every table is secured by Row‑Level Security (RLS).  Users can read their own profiles; lab owners and administrators can manage all lab data; other lab members enjoy read access and can create new items like whiteboard strokes, chat messages, or TODOs.

The README refers to the project as "remedi‑lab", emphasizing that it’s a tool for research labs to collaborate more effectively.  Key features highlighted in the component `SidebarRight.tsx` include AI‑generated citations powered by Perplexity (via `usePerplexity.ts`) and a reporting workflow (`useReportGeneration.ts`).  The sidebar hook `useResponsiveSidebar.ts` provides a mobile‑friendly navigation experience.

In short, this repository is the codebase for a modern, AI‑assisted, collaborative research workbench that blends a realtime database, React UI, and cloud‑native authentication and storage.