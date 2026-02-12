// ============================================================================
// routes.js - API HTTP (Express)
// ============================================================================

const express = require("express");
const fs = require("fs");
const path = require("path");
const mime = require("mime-types");
const wa = require("./wa");

const router = express.Router();

// ==================== MIDDLEWARE ====================
function requireApiKey(req, res, next) {
  const apiKey = req.headers["x-api-key"] || req.headers["X-API-Key"];
  const expectedKey = process.env.API_KEY;

  // Debug (remover em produção)
  console.log("🔐 Auth check:", {
    received: apiKey ? `${apiKey.substring(0, 10)}...` : "ausente",
    expected: expectedKey ? `${expectedKey.substring(0, 10)}...` : "ausente",
    match: apiKey === expectedKey,
  });

  if (!expectedKey) {
    return res.status(500).json({
      success: false,
      error: "API_KEY não configurada no servidor",
    });
  }

  if (!apiKey || apiKey !== expectedKey) {
    return res.status(401).json({
      success: false,
      error: "API Key inválida ou ausente",
      debug: {
        received: apiKey ? "presente" : "ausente",
        expected: expectedKey ? "presente" : "ausente",
      },
    });
  }

  next();
}

// Sessão por usuário: extrai X-Instance-Id (ex: user_123), default se ausente
function instanceId(req) {
  return req.headers["x-instance-id"] || req.headers["X-Instance-Id"] || "default";
}

// Health check (aberto, sem autenticação)
router.get("/health", (req, res) => {
  const instId = req.headers["x-instance-id"] || req.headers["X-Instance-Id"] || "default";
  const status = wa.getConnectionStatus(instId);
  res.json({
    status: "ok",
    whatsapp: {
      status: status,
      connected: status === "connected",
    },
    timestamp: new Date().toISOString(),
  });
});

// ==================== STATUS ====================
router.get("/v1/status", requireApiKey, (req, res) => {
  const instId = req.headers["x-instance-id"] || req.headers["X-Instance-Id"] || "default";
    const status = wa.getConnectionStatus(instId);
  const qr = wa.getQRCode(instId);
  
  res.json({
    connection: status,
    qr_available: qr !== null,
    socket_active: wa.getSocket(instId) !== null,
  });
});

// ==================== QR CODE ====================
router.get("/v1/qr", requireApiKey, async (req, res) => {
  const instId = req.headers["x-instance-id"] || req.headers["X-Instance-Id"] || "default";
  const qr = wa.getQRCode(instId);
  
  if (!qr) {
    return res.status(404).json({
      error: "QR Code não disponível",
      message: "A conexão já está estabelecida ou não foi solicitada",
    });
  }

  // Retorna QR code como imagem
  const base64Data = qr.replace(/^data:image\/png;base64,/, "");
  const imageBuffer = Buffer.from(base64Data, "base64");
  
  res.setHeader("Content-Type", "image/png");
  res.send(imageBuffer);
});

// ==================== CONECTAR ====================
router.post("/v1/connect", requireApiKey, async (req, res) => {
  try {
    const instId = req.headers["x-instance-id"] || req.headers["X-Instance-Id"] || "default";
    const status = wa.getConnectionStatus(instId);
    
    if (status === "connected") {
      return res.json({
        success: true,
        message: "Já está conectado",
        status: "connected",
      });
    }

    if (status === "connecting") {
      return res.json({
        success: true,
        message: "Conexão em andamento",
        status: "connecting",
      });
    }

    // Inicia conexão
    await wa.startSock(instId);
    
    res.json({
      success: true,
      message: "Conexão iniciada",
      status: wa.getConnectionStatus(instId),
    });
  } catch (error) {
    console.error("Erro ao conectar:", error);
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

// ==================== DESCONECTAR ====================
router.post("/v1/disconnect", requireApiKey, async (req, res) => {
  try {
    const instId = req.headers["x-instance-id"] || req.headers["X-Instance-Id"] || "default";
    await wa.disconnect(instId);
    
    res.json({
      success: true,
      message: "Desconectado",
    });
  } catch (error) {
    console.error("Erro ao desconectar:", error);
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

// ==================== RESET SESSÃO ====================
router.post("/v1/session/reset", requireApiKey, async (req, res) => {
  try {
    const instId = req.headers["x-instance-id"] || req.headers["X-Instance-Id"] || "default";
    // Desconecta primeiro
    await wa.disconnect(instId);
    
    // Remove arquivos de sessão
    const authDir = process.env.AUTH_DIR || "/data/auth";
    const sessionDir = instId === "default" ? path.join(authDir, "baileys-session") : path.join(authDir, "sessions", instId, "baileys-session");
    
    if (fs.existsSync(sessionDir)) {
      fs.rmSync(sessionDir, { recursive: true, force: true });
      console.log(`Sessão removida: ${sessionDir}`);
    }
    
    res.json({
      success: true,
      message: "Sessão resetada. Use /v1/connect para gerar novo QR code",
    });
  } catch (error) {
    console.error("Erro ao resetar sessão:", error);
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

// ==================== ENVIAR TEXTO ====================
router.post("/v1/send/text", requireApiKey, async (req, res) => {
  try {
    const instId = req.headers["x-instance-id"] || req.headers["X-Instance-Id"] || "default";
    const { to, text } = req.body;

    if (!to || !text) {
      return res.status(400).json({
        success: false,
        error: "Parâmetros 'to' e 'text' são obrigatórios",
      });
    }

    const sock = wa.getSocket(instId);
    
    if (!sock) {
      return res.status(503).json({
        success: false,
        error: "Socket não está conectado. Use /v1/connect primeiro",
      });
    }

    // Formata número para JID
    const jid = formatJID(to);
    
    const result = await sock.sendMessage(jid, { text });
    
    res.json({
      success: true,
      message_id: result.key.id,
      to: jid,
      status: "sent",
    });
  } catch (error) {
    console.error("Erro ao enviar mensagem:", error);
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

// ==================== ENVIAR IMAGEM ====================
router.post("/v1/send/image", requireApiKey, async (req, res) => {
  try {
    const { to, image_path, image_url, image_base64, caption } = req.body;

    if (!to) {
      return res.status(400).json({
        success: false,
        error: "Parâmetro 'to' é obrigatório",
      });
    }

    if (!image_path && !image_url && !image_base64) {
      return res.status(400).json({
        success: false,
        error: "É necessário fornecer 'image_path', 'image_url' ou 'image_base64'",
      });
    }

    const instId = req.headers["x-instance-id"] || req.headers["X-Instance-Id"] || "default";
    const sock = wa.getSocket(instId);
    
    if (!sock) {
      return res.status(503).json({
        success: false,
        error: "Socket não está conectado. Use /v1/connect primeiro",
      });
    }

    let imageBuffer;
    
    if (image_path) {
      if (!fs.existsSync(image_path)) {
        return res.status(404).json({
          success: false,
          error: `Arquivo não encontrado: ${image_path}`,
        });
      }
      imageBuffer = fs.readFileSync(image_path);
    } else if (image_url) {
      const https = require("https");
      const http = require("http");
      
      const client = image_url.startsWith("https") ? https : http;
      
      imageBuffer = await new Promise((resolve, reject) => {
        client.get(image_url, (response) => {
          const chunks = [];
          response.on("data", (chunk) => chunks.push(chunk));
          response.on("end", () => resolve(Buffer.concat(chunks)));
          response.on("error", reject);
        }).on("error", reject);
      });
    } else if (image_base64) {
      imageBuffer = Buffer.from(image_base64, "base64");
    }

    const jid = formatJID(to);
    
    const result = await sock.sendMessage(jid, {
      image: imageBuffer,
      caption: caption || "",
    });
    
    res.json({
      success: true,
      message_id: result.key.id,
      to: jid,
      status: "sent",
    });
  } catch (error) {
    console.error("Erro ao enviar imagem:", error);
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

// ==================== ENVIAR DOCUMENTO ====================
router.post("/v1/send/document", requireApiKey, async (req, res) => {
  try {
    const { to, document_path, document_url, document_base64, filename, caption } = req.body;

    if (!to) {
      return res.status(400).json({
        success: false,
        error: "Parâmetro 'to' é obrigatório",
      });
    }

    if (!document_path && !document_url && !document_base64) {
      return res.status(400).json({
        success: false,
        error: "É necessário fornecer 'document_path', 'document_url' ou 'document_base64'",
      });
    }

    const instId = req.headers["x-instance-id"] || req.headers["X-Instance-Id"] || "default";
    const sock = wa.getSocket(instId);
    
    if (!sock) {
      return res.status(503).json({
        success: false,
        error: "Socket não está conectado. Use /v1/connect primeiro",
      });
    }

    let documentBuffer;
    let finalFilename = filename;
    let mimeType = "application/octet-stream";
    
    if (document_path) {
      if (!fs.existsSync(document_path)) {
        return res.status(404).json({
          success: false,
          error: `Arquivo não encontrado: ${document_path}`,
        });
      }
      documentBuffer = fs.readFileSync(document_path);
      finalFilename = filename || path.basename(document_path);
      mimeType = mime.lookup(document_path) || "application/octet-stream";
    } else if (document_url) {
      const https = require("https");
      const http = require("http");
      
      const client = document_url.startsWith("https") ? https : http;
      
      documentBuffer = await new Promise((resolve, reject) => {
        client.get(document_url, (response) => {
          const chunks = [];
          response.on("data", (chunk) => chunks.push(chunk));
          response.on("end", () => resolve(Buffer.concat(chunks)));
          response.on("error", reject);
        }).on("error", reject);
      });
      
      if (!finalFilename) {
        const url = require("url");
        const parsed = url.parse(document_url);
        finalFilename = path.basename(parsed.pathname) || "document";
      }
      mimeType = mime.lookup(finalFilename) || "application/octet-stream";
    } else if (document_base64) {
      documentBuffer = Buffer.from(document_base64, "base64");
      if (!finalFilename) {
        finalFilename = "document";
      }
    }

    const jid = formatJID(to);
    
    const result = await sock.sendMessage(jid, {
      document: documentBuffer,
      fileName: finalFilename,
      mimetype: mimeType,
      caption: caption || "",
    });
    
    res.json({
      success: true,
      message_id: result.key.id,
      to: jid,
      status: "sent",
    });
  } catch (error) {
    console.error("Erro ao enviar documento:", error);
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

// ==================== UTILITÁRIOS ====================
function formatJID(number) {
  // Remove caracteres não numéricos
  const cleaned = number.replace(/\D/g, "");
  
  // Adiciona @s.whatsapp.net se não tiver
  if (cleaned.includes("@")) {
    return cleaned;
  }
  
  return `${cleaned}@s.whatsapp.net`;
}

module.exports = router;
