// ============================================================================
// index.js - Bootstrap do Serviço WhatsApp Gateway
// ============================================================================

require("dotenv").config();
const express = require("express");
const cors = require("cors");
const routes = require("./routes");
const wa = require("./wa");

const app = express();
const PORT = process.env.PORT || 8007;

// Middleware
app.use(cors());
app.use(express.json({ limit: "50mb" }));
app.use(express.urlencoded({ extended: true, limit: "50mb" }));

// Rotas
app.use("/", routes);

// Configura webhook URL se fornecido
if (process.env.WEBHOOK_URL) {
  wa.setWebhookUrl(process.env.WEBHOOK_URL);
  console.log(`📡 Webhook configurado: ${process.env.WEBHOOK_URL}`);
}

// Inicialização
async function startServer() {
  try {
    console.log("🚀 Iniciando WhatsApp Gateway Service...");
    console.log(`📡 Porta: ${PORT}`);
    console.log(`🔐 API Key: ${process.env.API_KEY ? "Configurada" : "NÃO CONFIGURADA"}`);
    console.log(`🔗 Webhook: ${process.env.WEBHOOK_URL || "Não configurado"}`);
    console.log(`📁 Auth Dir: ${process.env.AUTH_DIR || "/data/auth"}`);
    
    // Inicia servidor HTTP
    app.listen(PORT, "0.0.0.0", () => {
      console.log(`✅ Servidor rodando em http://0.0.0.0:${PORT}`);
      console.log(`📱 Endpoints disponíveis:`);
      console.log(`   GET  /health - Health check (aberto)`);
      console.log(`   GET  /v1/status - Status da conexão (x-api-key)`);
      console.log(`   GET  /v1/qr - QR Code (x-api-key)`);
      console.log(`   POST /v1/connect - Conectar WhatsApp (x-api-key)`);
      console.log(`   POST /v1/disconnect - Desconectar WhatsApp (x-api-key)`);
      console.log(`   POST /v1/session/reset - Resetar sessão (x-api-key)`);
      console.log(`   POST /v1/send/text - Enviar mensagem de texto (x-api-key)`);
      console.log(`   POST /v1/send/image - Enviar imagem (x-api-key)`);
      console.log(`   POST /v1/send/document - Enviar documento (x-api-key)`);
    });

    // Tenta conectar automaticamente se configurado
    if (process.env.AUTO_CONNECT === "true") {
      setTimeout(async () => {
        try {
          console.log("🔄 Tentando conectar automaticamente...");
          await wa.startSock();
        } catch (error) {
          console.error("Erro ao conectar automaticamente:", error);
        }
      }, 2000);
    }
  } catch (error) {
    console.error("❌ Erro ao iniciar servidor:", error);
    process.exit(1);
  }
}

// Inicia servidor
startServer();

// Tratamento de erros não capturados
process.on("unhandledRejection", (error) => {
  console.error("Unhandled Rejection:", error);
});

process.on("uncaughtException", (error) => {
  console.error("Uncaught Exception:", error);
  process.exit(1);
});
