const waitingForResponse = new Map();

function waitResponse(remoteJid, participant = null, timeout = 30000) {
  const chave = participant ? `${remoteJid}:${participant}` : remoteJid;

  return new Promise((resolve, reject) => {
    waitingForResponse.set(chave, resolve);

    setTimeout(() => {
      if (waitingForResponse.has(chave)) {
        waitingForResponse.delete(chave);
        reject(new Error("⏱️ Tempo esgotado."));
      }
    }, timeout);
  });
}

function processResponse(remoteJid, participant = null, texto) {
  const chave = participant ? `${remoteJid}:${participant}` : remoteJid;

  if (waitingForResponse.has(chave)) {
    const resolver = waitingForResponse.get(chave);
    waitingForResponse.delete(chave);
    resolver(texto);
    return true;
  }
  return false;
}

module.exports = { waitResponse, processResponse };
