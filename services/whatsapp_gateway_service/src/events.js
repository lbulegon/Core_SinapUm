// ============================================================================
// events.js - Configuração de Eventos Baileys (adaptado do bot-do-mago)
// ============================================================================

// libs externas
const qrcode = require("qrcode");
const mime = require("mime-types");

// libs node
const fs = require("fs");
const path = require("path");

// baileys
const { DisconnectReason } = require("baileys");

// configurações
const processedMessages = new Set();
const { processResponse } = require("./utils/waitMessage");

function eventsConfig(sock, saveCreds, callbacks = {}) {
  const {
    onQR = () => {},
    onConnected = () => {},
    onDisconnected = () => {},
    onMessage = () => {},
  } = callbacks;

  sock.ev.on("creds.update", saveCreds);

  sock.ev.on("messages.upsert", async ({ messages, type }) => {
    if (type === "notify" || type === "append") {
      for (const msg of messages) {
        // propriedades
        const idMensagem = msg.key.id;
        const text = (
          msg.message?.conversation ||
          msg.message?.extendedTextMessage?.text ||
          ""
        )
          .trim()
          .toLowerCase();
        const from = msg.key.remoteJid;
        const fromMe = msg.key.fromMe;
        const idUnico = msg.key.participant;

        // verifica se a mensagem já foi processada
        if (processedMessages.has(idMensagem)) continue;
        processedMessages.add(idMensagem);

        // Não processa mensagens próprias
        if (fromMe) continue;

        // verifica se a mensagem é de um grupo
        let number;
        if (msg.key.participant && msg.key.participantAlt) {
          number = msg.key.participantAlt.split("@")[0];
        } else if (msg.key.remoteJid && msg.key.remoteJid.includes("@")) {
          number = msg.key.remoteJid.split("@")[0];
        }

        // verifica se o texto da mensagem é válido
        if (!text || !from) continue;

        console.log(`${number}: ${text}`);

        // Prepara dados da mensagem
        const messageData = {
          id: idMensagem,
          from: from,
          isFromMe: fromMe,
          participant: idUnico,
          number: number,
          text: text,
          raw: msg,
        };

        // Notifica callback
        onMessage(messageData);

        // verifica se há resposta para a Promise
        const resolveu = processResponse(from, idUnico, text);
        if (resolveu) continue;
      }
    }
  });

  // bloco de código responsável pela reconexão com o websocket
  sock.ev.on("connection.update", async (update) => {
    const { connection, lastDisconnect, qr } = update;

    if (qr) {
      // Gera QR code como string base64
      try {
        const qrImage = await qrcode.toDataURL(qr);
        onQR(qrImage);
        console.log("📱 QR Code gerado. Use o endpoint /v1/qr para visualizar.");
      } catch (error) {
        console.error("Erro ao gerar QR code:", error);
      }
    }

    if (connection === "close") {
      const shouldReconnect =
        lastDisconnect?.error?.output?.statusCode !==
        DisconnectReason.loggedOut;

      console.log(
        "❌ conexão encerrada. ",
        shouldReconnect == true
          ? "reconectando"
          : "reconexão automática está desativada"
      );

      onDisconnected(shouldReconnect);
      // Reconexão é feita pelo callback onDisconnected em wa.js (com instanceId correto)
    }

    if (connection === "open") {
      console.log("✅ Conectado ao WhatsApp!");
      onConnected();
    }
  });
}

module.exports = { eventsConfig };
