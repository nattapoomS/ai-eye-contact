import { betterAuth } from "better-auth";
import { createPool } from "mysql2/promise";

export const auth = betterAuth({
  appName: "AI Eye Contact",
  database: createPool({
    host: process.env.DB_HOST ?? "localhost",
    port: Number(process.env.DB_PORT ?? 3307),
    user: process.env.DB_USER ?? "root",
    password: process.env.DB_PASSWORD ?? "",
    database: process.env.DB_NAME ?? "ai_eye_contact",
    timezone: "Z",
  }),
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false,
  },
});
