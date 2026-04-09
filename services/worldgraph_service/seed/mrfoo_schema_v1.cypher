// =============================================================================
// MrFoo Food Knowledge Graph (FKG) — Schema v1
// Subgrafo com labels MRFOO_* no WorldGraph (Neo4j) existente.
// Idempotente: MERGE e CREATE CONSTRAINT/INDEX IF NOT EXISTS.
// NÃO altera/remove seeds existentes (001_schema, 010_seed).
// =============================================================================

// --- Constraints (Neo4j 5: CREATE ... IF NOT EXISTS) ---
CREATE CONSTRAINT mrfoo_tenant_id IF NOT EXISTS FOR (n:MRFOO_Tenant) REQUIRE n.tenant_id IS UNIQUE;
CREATE CONSTRAINT mrfoo_menuitem_tenant_pg IF NOT EXISTS FOR (n:MRFOO_MenuItem) REQUIRE (n.tenant_id, n.pg_id) IS UNIQUE;
CREATE CONSTRAINT mrfoo_ingredient_tenant_pg IF NOT EXISTS FOR (n:MRFOO_Ingredient) REQUIRE (n.tenant_id, n.pg_id) IS UNIQUE;
CREATE CONSTRAINT mrfoo_order_tenant_pg IF NOT EXISTS FOR (n:MRFOO_Order) REQUIRE (n.tenant_id, n.pg_id) IS UNIQUE;

// --- Indexes (performance) ---
CREATE INDEX mrfoo_menuitem_tenant_name IF NOT EXISTS FOR (n:MRFOO_MenuItem) ON (n.tenant_id, n.name);
CREATE INDEX mrfoo_order_tenant_created IF NOT EXISTS FOR (n:MRFOO_Order) ON (n.tenant_id, n.created_at);
CREATE INDEX mrfoo_ingredient_tenant_name IF NOT EXISTS FOR (n:MRFOO_Ingredient) ON (n.tenant_id, n.name);

// --- TimeSlots fixos (idempotente) ---
MERGE (t:MRFOO_TimeSlot {code: 'ALMOCO'})
SET t.vertical = 'mrfoo',
    t.name = 'Almoço',
    t.start_hour = 11,
    t.end_hour = 14,
    t.updated_at = datetime();

MERGE (t:MRFOO_TimeSlot {code: 'JANTAR'})
SET t.vertical = 'mrfoo',
    t.name = 'Jantar',
    t.start_hour = 18,
    t.end_hour = 23,
    t.updated_at = datetime();

MERGE (t:MRFOO_TimeSlot {code: 'MADRUGADA'})
SET t.vertical = 'mrfoo',
    t.name = 'Madrugada',
    t.start_hour = 23,
    t.end_hour = 4,
    t.updated_at = datetime();
