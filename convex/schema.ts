// Convex Schema for Bella's Memory Database
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  // Client entities
  clients: defineTable({
    entity_id: v.string(),
    name: v.string(),
    email: v.optional(v.string()),
    phone: v.optional(v.string()),
    amount_owed: v.optional(v.number()),
    days_overdue: v.optional(v.number()),
    status: v.string(), // 'active', 'overdue', 'paid', 'blacklist'
    payment_rating: v.optional(v.number()),
    total_spent: v.optional(v.number()),
    services_used: v.optional(v.number()),
    last_service_date: v.optional(v.string()),
    notes: v.optional(v.string()),
    data: v.any(), // Full client data object
    updated_at: v.string(),
  })
    .index("by_entity_id", ["entity_id"])
    .index("by_status", ["status"])
    .index("by_amount_owed", ["amount_owed"]),

  // Invoice entities
  invoices: defineTable({
    entity_id: v.string(),
    invoice_number: v.optional(v.string()),
    client_id: v.string(),
    client_name: v.string(),
    amount: v.number(),
    status: v.string(), // 'unpaid', 'paid', 'overdue', 'cancelled'
    due_date: v.optional(v.string()),
    created_date: v.string(),
    paid_date: v.optional(v.string()),
    square_id: v.optional(v.string()),
    data: v.any(), // Full invoice data
    updated_at: v.string(),
  })
    .index("by_entity_id", ["entity_id"])
    .index("by_client", ["client_id"])
    .index("by_status", ["status"])
    .index("by_due_date", ["due_date"]),

  // Session summaries
  sessions: defineTable({
    entity_id: v.string(), // Date: YYYY-MM-DD
    date: v.string(),
    tasks_completed: v.array(v.string()),
    decisions_made: v.array(v.string()),
    outstanding_items: v.array(v.string()),
    financial_summary: v.optional(v.string()),
    client_interactions: v.array(v.string()),
    summary: v.string(),
    data: v.any(), // Full session data
    updated_at: v.string(),
  })
    .index("by_entity_id", ["entity_id"])
    .index("by_date", ["date"]),

  // Tasks/Reminders
  tasks: defineTable({
    entity_id: v.string(),
    description: v.string(),
    priority: v.string(), // 'high', 'medium', 'low'
    status: v.string(), // 'pending', 'in_progress', 'completed'
    due_date: v.optional(v.string()),
    related_client: v.optional(v.string()),
    related_invoice: v.optional(v.string()),
    data: v.any(),
    created_at: v.string(),
    updated_at: v.string(),
  })
    .index("by_entity_id", ["entity_id"])
    .index("by_status", ["status"])
    .index("by_priority", ["priority"])
    .index("by_due_date", ["due_date"]),

  // Memory chunks (for large data)
  memory_chunks: defineTable({
    parent_id: v.string(), // Related entity
    parent_type: v.string(), // 'client', 'session', etc.
    chunk_index: v.number(),
    content: v.string(),
    summary: v.optional(v.string()),
    created_at: v.string(),
  })
    .index("by_parent", ["parent_id", "parent_type"])
    .index("by_parent_and_index", ["parent_id", "chunk_index"]),
});
