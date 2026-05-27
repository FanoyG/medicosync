# MedicoSync — Frontend

A modern medical records platform for doctors. React + Vite frontend, designed to deploy on Netlify with a backend on Render.

## Local Development

```bash
npm install
npm run dev
```

Create a `.env` file:
```
VITE_API_URL=https://medicosync-backend.onrender.com
```

## Deploy to Netlify via GitHub

1. Push this folder to a new GitHub repo
2. Go to [app.netlify.com](https://app.netlify.com) → **Add new site** → **Import from Git**
3. Choose your GitHub repo
4. Build settings are auto-detected from `netlify.toml`:
   - **Build command:** `npm run build`
   - **Publish directory:** `dist`
5. Go to **Site configuration → Environment variables** and add:
   - `VITE_API_URL` = `https://medicosync-backend.onrender.com`
6. Click **Deploy site**

## Environment Variables

| Variable | Description |
|---|---|
| `VITE_API_URL` | Base URL of your backend API (e.g. `https://medicosync-backend.onrender.com`) |

## Tech Stack

- React 19 + TypeScript
- Vite 6
- Tailwind CSS v4
- TanStack Query (React Query)
- Wouter (routing)
- shadcn/ui components
- Framer Motion
