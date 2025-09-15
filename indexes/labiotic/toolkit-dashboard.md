# 📊 Dashboard – This Project

| 🎯 | **Summary** | 🛡️ | **Potential Vulnerabilities** | 🔄 | **Stale Dependencies** | 💡 | **Suggestions** |
|----|-------------|----|------------------------------|----|------------------------|----|-----------------|
| **Purpose** | Web‑based AI research lab platform that integrates Supabase, Google GenAI, and a rich React UI for collaborative whiteboarding, molecule visualization, and AI‑powered research workflows. | • **Supabase** – exposed config may leak API keys if not secured. <br>• **Google GenAI** – depends on API key; can allow unauthorized calls if key is compromised. <br>• **`axios`** – no global timeout or error handling → injection risk via malformed responses. <br>• **`file-saver` + `docx`** – file generation could be abused for malicious content. | • **`@google/generative-ai`** v0.21 → newer security patches unavailable. <br>• **`@supabase/supabase-js`** v2.39 may miss critical bug fixes. <br>• **`axios`** v1.9, `file-saver` v2.0.5 – stable but rarely updated. | • **`react`** 18.3.1 – still a major release; newer patches exist. <br>• **`react-dom`** 18.3.1 – same. <br>• **`postcss`, `tailwindcss`, `typescript`** – latest versions available but not critical. | • **Linting** – ESLint extends recommended but missing some rules (e.g., security). <br>• **Testing** – no unit/integration tests identified. <br>• **CI/CD** – no pipeline configured. | • Add explicit **environment variable protection** and **role‑based access** in Supabase rules. <br>• Enforce **CSP** and **sanitize** all user inputs. <br>• Convert key API calls to a **backend service** or *edge functions* that can enforce rate‑limits. <br>• Implement a **global error boundary** for React components. <br>• Add **unit tests** for critical hooks (`useAuth`, `usePerplexity`). <br>• Include a **CI pipeline** (GitHub Actions) for linting, building, and running tests. <br>• Document **deployment steps** and **environment variables** in a README. <br>• Add **semantic version constraints** and enable `npm audit`. |

---

## 📖 About the Project

- **Stack**  
  - **UI**: React 18 + TypeScript, Tailwind CSS, Vite.  
  - **Styling**: Rich animations, SVG icons, and custom CSS.  
  - **Backend**: Supabase (Postgres), Google Generative AI for NLP & modeling.  
  - **Utilities**: Axios for HTTP, `docx` & `file-saver` for generating reports.  
  - **Build & Lint**: Vite, ESLint (typescript‑eslint), Tailwind, PostCSS.

- **Key Features**  
  - Auth flow (`AuthPage.tsx`) with Supabase integration.  
  - Dashboard & Lab management components (`Dashboard.tsx`, `LabDashboard.tsx`).  
  - Rich research module with AI‑powered chat, visualizers (amino acids, compounds), and report generation.  
  - Collaborative whiteboard (`Whiteboard.tsx`, `WhiteboardCanvas.tsx`).  
  - Responsive design with custom sidebars (`useResponsiveSidebar` hook).

- **Architecture Highlights**  
  - Functional, component‑centric React (hooks for side‑effects).  
  - Modular folder layout (`components/`, `hooks/`, `lib/`, `types/`).  
  - Uses TypeScript for static typing throughout.  
  - Uses Vite's module resolution; some polyfills are excluded (`lucide-react`).  
  - Extensive use of custom hooks for auth, AI, reporting, and sidebar handling.

---

## ⚡️ Vulnerability Summary

| Component | Potential Attack Surface | Mitigations Needed |
|-----------|------------------------|--------------------|
| **Supabase** | Direct client‑side calls expose API keys → can be used to manipulate database. | Store keys in environment variables on a backend; use Supabase Auth and Row‑Level Security (RLS). |
| **Google GenAI** | Exposing API key in the app allows misuse and unnecessary bill. | Proxy via serverless function; add request quotas. |
| **Axios** | No timeout or response validation → denial of service or XSS via blob data. | Add generic timeout and response schema validation. |
| **File Generation** | Generated `docx`/files could include malicious content or allow mass download attacks. | Enforce size limits; sanitise inputs; throttle download requests. |
| **React** | Potential untrusted user input injection → XSS. | Escape all dynamic content, use `dangerouslySetInnerHTML` only when sanitized. |
| **SVG Animations** | SVGs accept attributes; could be hijacked if user‑generated content. | Validate SVG source or use static assets from trusted source. |

---

## 🕰️ Stale and Suspect Dependencies

| Package | Current Version | Latest Noted Version (as of 2025‑09) | Risk |
|---------|-----------------|--------------------------------------|------|
| `react` / `react-dom` | 18.3.1 | 18.4.x | Minor – may contain bug fixes. |
| `@supabase/supabase-js` | 2.39.0 | 2.45.x | Security patches; consider upgrading. |
| `axios` | 1.9.0 | 1.10.x | Patch updates; upgrade for bug fixes. |
| `docx`, `file-saver` | 8.5.0 / 2.0.5 | 8.7.x / 2.1.x | Add patch versions. |
| `tailwindcss` | 3.4.1 | 3.5.x | Minor style changes, performance. |
| `typescript` | 5.5.3 | 5.6.x | Minor improvements; no major breaking. |
| `eslint`, plugins | 9.9.1 | 9.10.x | Minor lint rule changes. |

> **Recommendation**: Run `npm outdated` and `npm audit` locally. Update non‑breaking minor/patch releases. Implement a version lock policy (`npm ci`).

---

## 🏗️ Code Quality & Best Practices

| Area | Observation | Score (✦/5) |
|------|-------------|--------------|
| **Type Safety** | Types used throughout; hooks and components declare props/returns. | 4/5 |
| **Component Structure** | Large components (Dashboard, LabDashboard) bundle many concerns; could be refactored into smaller atomic components. | 3/5 |
| **State Management** | Local React state only; no global store. Good for current size but may hinder scalability. | 4/5 |
| **Security** | No CSP, limited to client‑side only; missing role checks on Supabase reads/writes. | 2/5 |
| **Performance** | Heavy SVG & animation usage; all inlined. Might be fine but consider lazy‑loading large assets. | 3/5 |
| **Testing** | No test files found. | 0/5 |
| **Documentation** | README is minimal; no contribution guidelines, code comments. | 2/5 |

> **Overall**: 16/35

---

## 👋 Onboarding Guide for New Developers

1. **Prerequisites**  
   - Node.js 20.x (or LTS compatible).  
   - Git and familiarity with GitHub.  
   - Supabase account (if working with DB) and a Google GenAI API key.

2. **Set Up Local Environment**  
   ```bash
   git clone <repo-url>
   cd emon69420-labiotic
   cp .env.example .env   # fill in SUPABASE_URL, SUPABASE_ANON_KEY, GENAI_KEY
   npm ci                 # install dependencies
   npm run dev             # start dev server
   ```

3. **Project Structure Overview**  
   - `src/` – core React code.  
   - `components/` – presentational logic.  
   - `hooks/` – reusable logic.  
   - `lib/` – external library wrappers (Supabase).  
   - `types/` – TS type definitions.  
   - `vite.config.ts` – build config.  
   - `postcss.config.js`, `tailwind.config.js` – styling.  

4. **Core Workflows**  
   - **Auth** – `useAuth` hook + `AuthPage`.  
   - **Lab Management** – `Dashboard`, `LabDashboard`.  
   - **Research Engine** – sub‑components under `components/research`.  
   - **Whiteboard** – collaborative drawing.  

5. **Running Tests (once added)**  
   ```bash
   npm test
   ```
   - Add test suites in `src/__tests__/`.

