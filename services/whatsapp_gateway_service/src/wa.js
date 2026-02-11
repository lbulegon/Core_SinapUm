// ============================================================================
// wa.js - Lógica Baileys (adaptada do bot-do-mago)
// ============================================================================
// Este arquivo contém a lógica principal do WhatsApp usando Baileys.
// Derivado diretamente de /root/Source/bot-do-mago

// bloquear logs internos
require("./utils/filterLogs")();

// baileys
const P = require("pino");
const {
  default: makeWASocket,
  fetchLatestBaileysVersion,
  makeCacheableSignalKeyStore,
} = require("baileys");

// módulos internos
const { getAuthState } = require("./auth");
const { eventsConfig } = require("./events");

// cache para controle interno do baileys
const { NodeCache } = require("@cacheable/node-cache");
const msgRetryCounterCache = new NodeCache();

// Estado global
let globalSock = null;
let isConnecting = false;
let connectionStatus = "disconnected"; // disconnected, connecting, connected, qr_required
let qrCode = null;
let webhookUrl = null;

// Callbacks para eventos
const eventCallbacks = {
  qr: [],
  connected: [],
  disconnected: [],
  message: [],
};

function addEventListener(event, callback) {
  if (eventCallbacks[event]) {
    eventCallbacks[event].push(callback);
  }
}

function removeEventListener(event, callback) {
  if (eventCallbacks[event]) {
    eventCallbacks[event] = eventCallbacks[event].filter(cb => cb !== callback);
  }
}

function notifyEvent(event, data) {
  if (eventCallbacks[event]) {
    eventCallbacks[event].forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        console.error(`Erro ao executar callback de evento ${event}:`, error);
      }
    });
  }
}

async function startSock() {
  if (isConnecting) {
    console.log("⚠️ Conexão já em andamento...");
    return globalSock;
  }

  if (globalSock && connectionStatus === "connected") {
    console.log("✅ Já está conectado");
    return globalSock;
  }

  isConnecting = true;
  connectionStatus = "connecting";

  try {
    const { state, saveCreds } = await getAuthState();
    const { version, isLatest } = await fetchLatestBaileysVersion();
    
    console.log(
      `💻 versão do websocket v${version[0]}.${version[1]}\n💻 última versão: ${
        isLatest == true ? "sim" : "não"
      }`
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

    globalSock = sock;
    
    // Configura eventos (passa callbacks)
    eventsConfig(sock, saveCreds, {
      onQR: (qr) => {
        qrCode = qr;
        connectionStatus = "qr_required";
        notifyEvent("qr", { qr });
        sendWebhook("qr", { qr });
      },
      onConnected: () => {
        connectionStatus = "connected";
        isConnecting = false;
        qrCode = null;
        notifyEvent("connected", {});
        sendWebhook("connected", {});
      },
      onDisconnected: (shouldReconnect) => {
        connectionStatus = "disconnected";
        isConnecting = false;
        notifyEvent("disconnected", { shouldReconnect });
        sendWebhook("disconnected", { shouldReconnect });
        
        if (shouldReconnect) {
          setTimeout(() => {
            startSock().catch(err => {
              console.error("Erro ao reconectar:", err);
            });
          }, 5000);
        }
      },
      onMessage: (messageData) => {
        notifyEvent("message", messageData);
        sendWebhook("message", messageData);
      },
    });
    
    return sock;
  } catch (error) {
    console.error("❌ Erro ao iniciar socket:", error);
    isConnecting = false;
    connectionStatus = "disconnected";
    throw error;
  }
}

function getSocket() {
  return globalSock;
}

function getConnectionStatus() {
  return connectionStatus;
}

function getQRCode() {
  return qrCode;
}

function setWebhookUrl(url) {
  webhookUrl = url;
}

async function sendWebhook(eventType, payload) {
  if (!webhookUrl) {
    return;
  }

  try {
    const https = require("https");
    const http = require("http");
    const url = require("url");
    
    const parsedUrl = url.parse(webhookUrl);
    const client = parsedUrl.protocol === "https:" ? https : http;
    
    const postData = JSON.stringify({
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
        resolve(); // Não falha o processo se webhook falhar
      });
      req.write(postData);
      req.end();
    });
  } catch (error) {
    console.error(`Erro ao enviar webhook para ${webhookUrl}:`, error.message);
  }
}

async function disconnect() {
  if (globalSock) {
    try {
      await globalSock.end();
    } catch (error) {
      console.error("Erro ao desconectar:", error);
    }
    globalSock = null;
  }
  connectionStatus = "disconnected";
  isConnecting = false;
  qrCode = null;
}

module.exports = {
  startSock,
  getSocket,
  getConnectionStatus,
  getQRCode,
  setWebhookUrl,
  disconnect,
  addEventListener,
  removeEventListener,
};
