# Drizzle Studio Setup

This folder contains a minimal Node.js project for exploring the PostgreSQL database that powers the Django app.

## 1. Install dependencies

```powershell
cd drizzle
npm install
```

## 2. Configure credentials

Option A – reuse the main `.env` at the project root (default behavior).  
Option B – copy the sample file and edit the values:

```powershell
copy .env.drizzle.example .env
```

You can also point to a different env file by exporting `DRIZZLE_ENV` before running commands (e.g. `set DRIZZLE_ENV=.env.local`).

## 3. Launch Drizzle Studio (visual explorer)

```powershell
npm run drizzle:studio
```

This spins up Drizzle Studio locally (default http://127.0.0.1:4983). The UI lists every schema/table, lets you browse rows, apply filters, and run ad-hoc SQL.

## 4. (Optional) Introspect schema into TypeScript

```powershell
npm run drizzle:introspect
```

The introspected schema is saved to `drizzle/schema.ts` so you have a typed snapshot of the latest database structure.

## Troubleshooting

- **Connection refused**: verify PostgreSQL is running and the credentials match your Django `.env` file.
- **SSL / remote DBs**: add additional connection parameters directly in `DATABASE_URL`.
- **Multiple environments**: set `DRIZZLE_ENV` to point at different env files per environment.
