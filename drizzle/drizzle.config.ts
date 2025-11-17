import { defineConfig } from "drizzle-kit";
import path from "node:path";
import dotenv from "dotenv";

const envFile = process.env.DRIZZLE_ENV ?? ".env";
dotenv.config({ path: path.resolve(process.cwd(), envFile) });

const {
  DATABASE_URL,
  DB_HOST = "localhost",
  DB_PORT = "5432",
  DB_USER = "sme_admin",
  DB_PASSWORD = "",
  DB_NAME = "sme_dashboard",
} = process.env;

const encodedPassword = encodeURIComponent(DB_PASSWORD ?? "");
const fallbackUrl = `postgresql://${DB_USER}:${encodedPassword}@${DB_HOST}:${DB_PORT}/${DB_NAME}`;
const connectionString = DATABASE_URL ?? fallbackUrl;

if (!connectionString) {
  throw new Error(
    "Set DATABASE_URL or DB_* variables so Drizzle can connect to PostgreSQL."
  );
}

export default defineConfig({
  schema: "./schema.ts",
  out: "./migrations",
  dialect: "postgresql",
  dbCredentials: {
    url: connectionString,
  },
  strict: true,
  verbose: true,
});
