function eventsAudit(sock) {
  // Auditoria de Eventos
  sock.ev.process(async (events) => {
    for (const key in events) {
      console.log(`📡 Evento detectado: ${key}`);
      eventName = "messages.upsert";
      if (key == eventName) {
        console.log(
          `event type "${eventName}" - result: ${JSON.stringify(
            events[key],
            null,
            2
          )}`
        );
      }
    }
  });
}

module.exports = { eventsAudit };
