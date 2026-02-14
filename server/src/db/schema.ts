import { pgTable, serial, text, doublePrecision, timestamp, boolean } from 'drizzle-orm/pg-core';

export const simulationLogs = pgTable('simulation_logs', {
  id: serial('id').primaryKey(),
  user_id: text('user_id').notNull(), // Placeholder for auth system
  ac_setpoint: doublePrecision('ac_setpoint').notNull(),
  reduction_factor: doublePrecision('reduction_factor').notNull(),
  projected_savings_inr: doublePrecision('projected_savings_inr'),
  carbon_reduction_kg: doublePrecision('carbon_reduction_kg'),
  comfort_score: doublePrecision('comfort_score'),
  created_at: timestamp('created_at').defaultNow(),
});

export const auditEvents = pgTable('audit_events', {
  id: serial('id').primaryKey(),
  event_type: text('event_type').notNull(),
  details: text('details'),
  timestamp: timestamp('timestamp').defaultNow(),
});