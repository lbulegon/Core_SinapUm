// ============================================================================
// wa.js - Lógica Baileys com suporte a multi-instância (X-Instance-Id)
// ============================================================================

require("./utils/filterLogs")();

const P = require("pino");
const {
  default: makeWASocket,
  fetchLatestBaileysVersion,
  makeCacheableSignalKeyStore,
} = require("baileys");

const { getAuthState } = require("./auth");
const { eventsConfig } = require("./events");

const { NodeCache } = require("@cacheable/node-cache");
const msgRetryCounterCache = new NodeCache();

let webhookUrl = null;

// Store por instância: instanceId -> { sock, isConnecting, connectionStatus, qrCode }
const instances = new Map();

function getInstance(instanceId = "default") {
  if (!instances.has(instanceId)) {
    instances.set(instanceId, {
      sock: null,
      isConnecting: false,
      connectionStatus: "disconnected",
      qrCode: null,
    });
  }
  return instances.get(instanceId);
}

async function startSock(instanceId = "default") {
  const inst = getInstance(instanceId);

  if (inst.isConnecting) {
    console.log(`[${instanceId}] ⚠️ Conexão já em andamento...`);
    return inst.sock;
  }

  if (inst.sock && inst.connectionStatus === "connected") {
    console.log(`[${instanceId}] ✅ Já está conectado`);
    return inst.sock;
  }

  inst.isConnecting = true;
  inst.connectionStatus = "connecting";

  try {
    const { state, saveCreds } = await getAuthState(instanceId);
    const { version, isLatest } = await fetchLatestBaileysVersion();

    console.log(
      `[${instanceId}] 💻 versão websocket v${version[0]}.${version[1]} (última: ${isLatest ? "sim" : "não"})`
    );

    const sock = makeWASocket({
      version,
      auth: {
        creds: state.creds,
        keys: makeCacheableSignalKeyStore(state.keys),
      },
      msgRetryCounterCache,
      generateHighQualityLinkPreview: true,
      logger: P({ level: "silent" }),
    });

    inst.sock = sock;

    eventsConfig(sock, saveCreds, {
      onQR: (qr) => {
        inst.qrCode = qr;
        inst.connectionStatus = "qr_required";
        sendWebhook(instanceId, "qr", { qr });
      },
      onConnected: () => {
        inst.connectionStatus = "connected";
        inst.isConnecting = false;
        inst.qrCode = null;
        sendWebhook(instanceId, "connected", {});
      },
      onDisconnected: (shouldReconnect) => {
        inst.connectionStatus = "disconnected";
        inst.isConnecting = false;
        inst.sock = null;
        sendWebhook(instanceId, "disconnected", { shouldReconnect });

        if (shouldReconnect) {
          setTimeout(() => {
            startSock(instanceId).catch((err) => {
              console.error(`[${instanceId}] Erro ao reconectar:`, err);
            });
          }, 5000);
        }
      },
      onMessage: (messageData) => {
        sendWebhook(instanceId, "message", messageData);
      },
    });

    return sock;
  } catch (error) {
    console.error(`[${instanceId}] ❌ Erro ao iniciar socket:`, error);
    inst.isConnecting = false;
    inst.connectionStatus = "disconnected";
    throw error;
  }
}

function getSocket(instanceId = "default") {
  return getInstance(instanceId).sock;
}

function getConnectionStatus(instanceId = "default") {
  return getInstance(instanceId).connectionStatus;
}

function getQRCode(instanceId = "default") {
  return getInstance(instanceId).qrCode;
}

function setWebhookUrl(url) {
  webhookUrl = url;
}

async function sendWebhook(instanceId, eventType, payload) {
  if (!webhookUrl) return;

  try {
    const https = require("https");
    const http = require("http");
    const url = require("url");

    const parsedUrl = url.parse(webhookUrl);
    const client = parsedUrl.protocol === "https:" ? https : http;

    const postData = JSON.stringify({
      instance_id: instanceId,
      event_type: eventType,
      payload: payload,
      ts: new Date().toISOString(),
    });

    const options = {
      hostname: parsedUrl.hostname,
      port: parsedUrl.port || (parsedUrl.protocol === "https:" ? 443 : 80),
      path: parsedUrl.path,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Content-Length": Buffer.byteLength(postData),
        "X-API-Key": process.env.API_KEY || "",
      },
    };

    await new Promise((resolve, reject) => {
      const req = client.request(options, (res) => {
        res.on("data", () => {});
        res.on("end", resolve);
      });
      req.on("error", (error) => {
        console.error(`Erro ao enviar webhook:`, error.message);
        resolve();
      });
      req.write(postData);
      req.end();
    });
  } catch (error) {
    console.error(`Erro ao enviar webhook para ${webhookUrl}:`, error.message);
  }
}

async function disconnect(instanceId = "default") {
  const inst = getInstance(instanceId);
  if (inst.sock) {
    try {
      await inst.sock.end();
    } catch (error) {
      console.error(`[${instanceId}] Erro ao desconectar:`, error);
    }
    inst.sock = null;
  }
  inst.connectionStatus = "disconnected";
  inst.isConnecting = false;
  inst.qrCode = null;
}

module.exports = {
  startSock,
  getSocket,
  getConnectionStatus,
  getQRCode,
  setWebhookUrl,
  disconnect,
  getInstance,
};
