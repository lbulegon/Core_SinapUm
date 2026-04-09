// ============================================================================
// eventBusPublisher.js - Publica eventos no Redis Streams (Event Bus)
// ============================================================================
// Quando EVENT_BUS_ENABLED=true, publica em redis://.../whatsapp.inbound
// Mantém webhook como opcional para compatibilidade.

let redisClient = null;

function getRedisClient() {
  if (redisClient) return redisClient;
  try {
    const Redis = require("ioredis");
    const url = process.env.REDIS_URL || "redis://localhost:6379/0";
    redisClient = new Redis(url);
    return redisClient;
  } catch (e) {
    console.error("[EventBus] Redis not available:", e.message);
    return null;
  }
}

function isEventBusEnabled() {
  return process.env.EVENT_BUS_ENABLED === "true" || process.env.EVENT_BUS_ENABLED === "1";
}

const STREAM_WHATSAPP_INBOUND = "whatsapp.inbound";

async function publishToEventBus(instanceId, eventType, payload) {
  if (!isEventBusEnabled()) return;

  const client = getRedisClient();
  if (!client) return;

  try {
    const event = `whatsapp.${eventType}`;
    const payloadStr = typeof payload === "object" ? JSON.stringify(payload) : String(payload);
    const fields = [
      "event", event,
      "instance_id", instanceId,
      "payload", payloadStr,
      "timestamp", new Date().toISOString(),
      "source", "whatsapp_gateway_service",
    ];
    if (payload && typeof payload === "object" && payload.from) {
      fields.push("jid", payload.from);
    }
    await client.xadd(STREAM_WHATSAPP_INBOUND, "*", ...fields);
    console.log(`[EventBus] Published ${event} to ${STREAM_WHATSAPP_INBOUND}`);
  } catch (e) {
    console.error("[EventBus] Publish error:", e.message);
  }
}

module.exports = { publishToEventBus, isEventBusEnabled };
