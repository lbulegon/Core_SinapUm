const { useMultiFileAuthState } = require("baileys");
const path = require("path");

// Diretório de autenticação (montado como volume Docker)
const AUTH_DIR = process.env.AUTH_DIR || "/data/auth";

async function getAuthState() {
  return await useMultiFileAuthState(
    path.join(AUTH_DIR, "baileys-session")
  );
}

module.exports = { getAuthState };
