const { useMultiFileAuthState } = require("baileys");
const path = require("path");
const fs = require("fs");

// Diretório de autenticação (montado como volume Docker)
const AUTH_DIR = process.env.AUTH_DIR || "/data/auth";

/**
 * Obtém auth state para uma instância.
 * @param {string} instanceId - ID da instância (ex: "default", "user_123")
 * @returns {Promise<{state: object, saveCreds: function}>}
 */
async function getAuthState(instanceId = "default") {
  const sessionDir =
    instanceId === "default"
      ? path.join(AUTH_DIR, "baileys-session")
      : path.join(AUTH_DIR, "sessions", instanceId, "baileys-session");

  const parentDir = path.dirname(sessionDir);
  if (!fs.existsSync(parentDir)) {
    fs.mkdirSync(parentDir, { recursive: true });
  }

  return await useMultiFileAuthState(sessionDir);
}

module.exports = { getAuthState };
