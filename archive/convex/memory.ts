// Convex functions for Bella's memory management
import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

// ============== STORE OPERATIONS ==============

export const storeClient = mutation({
  args: {
    entity_id: v.string(),
    data: v.any(),
  },
  handler: async (ctx, args) => {
    const existing = await ctx.db
      .query("clients")
      .withIndex("by_entity_id", (q) => q.eq("entity_id", args.entity_id))
      .first();

    const clientData = {
      entity_id: args.entity_id,
      name: args.data.name || args.entity_id,
      email: args.data.email,
      phone: args.data.phone,
      amount_owed: args.data.amount_owed || 0,
      days_overdue: args.data.days_overdue || 0,
      status: args.data.status || 'active',
      payment_rating: args.data.payment_rating,
      total_spent: args.data.total_spent,
      services_used: args.data.services_used,
      last_service_date: args.data.last_service_date,
      notes: args.data.notes,
      data: args.data,
      updated_at: new Date().toISOString(),
    };

    if (existing) {
      await ctx.db.patch(existing._id, clientData);
      return { success: true, action: "updated", id: existing._id };
    } else {
      const id = await ctx.db.insert("clients", clientData);
      return { success: true, action: "created", id };
    }
  },
});

export const storeInvoice = mutation({
  args: {
    entity_id: v.string(),
    data: v.any(),
  },
  handler: async (ctx, args) => {
    const existing = await ctx.db
      .query("invoices")
      .withIndex("by_entity_id", (q) => q.eq("entity_id", args.entity_id))
      .first();

    const invoiceData = {
      entity_id: args.entity_id,
      invoice_number: args.data.invoice_number,
      client_id: args.data.client_id || '',
      client_name: args.data.client_name || '',
      amount: args.data.amount || 0,
      status: args.data.status || 'unpaid',
      due_date: args.data.due_date,
      created_date: args.data.created_date || new Date().toISOString().split('T')[0],
      paid_date: args.data.paid_date,
      square_id: args.data.square_id,
      data: args.data,
      updated_at: new Date().toISOString(),
    };

    if (existing) {
      await ctx.db.patch(existing._id, invoiceData);
      return { success: true, action: "updated", id: existing._id };
    } else {
      const id = await ctx.db.insert("invoices", invoiceData);
      return { success: true, action: "created", id };
    }
  },
});

export const storeSession = mutation({
  args: {
    entity_id: v.string(),
    data: v.any(),
  },
  handler: async (ctx, args) => {
    const existing = await ctx.db
      .query("sessions")
      .withIndex("by_entity_id", (q) => q.eq("entity_id", args.entity_id))
      .first();

    const sessionData = {
      entity_id: args.entity_id,
      date: args.data.date || args.entity_id,
      tasks_completed: args.data.tasks_completed || [],
      decisions_made: args.data.decisions_made || [],
      outstanding_items: args.data.outstanding_items || [],
      financial_summary: args.data.financial_summary,
      client_interactions: args.data.client_interactions || [],
      summary: args.data.summary || '',
      data: args.data,
      updated_at: new Date().toISOString(),
    };

    if (existing) {
      await ctx.db.patch(existing._id, sessionData);
      return { success: true, action: "updated", id: existing._id };
    } else {
      const id = await ctx.db.insert("sessions", sessionData);
      return { success: true, action: "created", id };
    }
  },
});

export const storeTask = mutation({
  args: {
    entity_id: v.string(),
    data: v.any(),
  },
  handler: async (ctx, args) => {
    const taskData = {
      entity_id: args.entity_id,
      description: args.data.description || '',
      priority: args.data.priority || 'medium',
      status: args.data.status || 'pending',
      due_date: args.data.due_date,
      related_client: args.data.related_client,
      related_invoice: args.data.related_invoice,
      data: args.data,
      created_at: args.data.created_at || new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    const id = await ctx.db.insert("tasks", taskData);
    return { success: true, action: "created", id };
  },
});

// ============== GET OPERATIONS ==============

export const getClient = query({
  args: { entity_id: v.string() },
  handler: async (ctx, args) => {
    const client = await ctx.db
      .query("clients")
      .withIndex("by_entity_id", (q) => q.eq("entity_id", args.entity_id))
      .first();
    return client;
  },
});

export const getInvoice = query({
  args: { entity_id: v.string() },
  handler: async (ctx, args) => {
    const invoice = await ctx.db
      .query("invoices")
      .withIndex("by_entity_id", (q) => q.eq("entity_id", args.entity_id))
      .first();
    return invoice;
  },
});

export const getSession = query({
  args: { entity_id: v.string() },
  handler: async (ctx, args) => {
    const session = await ctx.db
      .query("sessions")
      .withIndex("by_entity_id", (q) => q.eq("entity_id", args.entity_id))
      .first();
    return session;
  },
});

// ============== SEARCH OPERATIONS ==============

export const searchClients = query({
  args: {
    status: v.optional(v.string()),
    limit: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    let query = ctx.db.query("clients");

    if (args.status) {
      query = query.withIndex("by_status", (q) => q.eq("status", args.status));
    }

    const results = await query
      .order("desc")
      .take(args.limit || 50);

    return results;
  },
});

export const getOverdueInvoices = query({
  args: {},
  handler: async (ctx) => {
    const invoices = await ctx.db
      .query("invoices")
      .withIndex("by_status", (q) => q.eq("status", "overdue"))
      .collect();

    return invoices;
  },
});

export const getPendingTasks = query({
  args: {},
  handler: async (ctx) => {
    const tasks = await ctx.db
      .query("tasks")
      .withIndex("by_status", (q) => q.eq("status", "pending"))
      .order("desc")
      .collect();

    return tasks;
  },
});

export const getRecentSessions = query({
  args: { limit: v.optional(v.number()) },
  handler: async (ctx, args) => {
    const sessions = await ctx.db
      .query("sessions")
      .order("desc")
      .take(args.limit || 10);

    return sessions;
  },
});

// ============== DELETE OPERATIONS ==============

export const deleteClient = mutation({
  args: { entity_id: v.string() },
  handler: async (ctx, args) => {
    const client = await ctx.db
      .query("clients")
      .withIndex("by_entity_id", (q) => q.eq("entity_id", args.entity_id))
      .first();

    if (client) {
      await ctx.db.delete(client._id);
      return { success: true, message: "Client deleted" };
    }
    return { success: false, message: "Client not found" };
  },
});

export const deleteSession = mutation({
  args: { entity_id: v.string() },
  handler: async (ctx, args) => {
    const session = await ctx.db
      .query("sessions")
      .withIndex("by_entity_id", (q) => q.eq("entity_id", args.entity_id))
      .first();

    if (session) {
      await ctx.db.delete(session._id);
      return { success: true, message: "Session deleted" };
    }
    return { success: false, message: "Session not found" };
  },
});

// ============== BULK OPERATIONS ==============

export const getAllOverdueClients = query({
  args: {},
  handler: async (ctx) => {
    const clients = await ctx.db
      .query("clients")
      .withIndex("by_status", (q) => q.eq("status", "overdue"))
      .collect();

    return clients;
  },
});

export const getFinancialSummary = query({
  args: {},
  handler: async (ctx) => {
    const overdueInvoices = await ctx.db
      .query("invoices")
      .withIndex("by_status", (q) => q.eq("status", "overdue"))
      .collect();

    const unpaidInvoices = await ctx.db
      .query("invoices")
      .withIndex("by_status", (q) => q.eq("status", "unpaid"))
      .collect();

    const totalOverdue = overdueInvoices.reduce((sum, inv) => sum + inv.amount, 0);
    const totalUnpaid = unpaidInvoices.reduce((sum, inv) => sum + inv.amount, 0);

    return {
      total_overdue: totalOverdue,
      total_unpaid: totalUnpaid,
      overdue_count: overdueInvoices.length,
      unpaid_count: unpaidInvoices.length,
    };
  },
});
