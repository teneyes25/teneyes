import { createApp } from "./app.js";
import { config } from "./config.js";
import { ensureAgentMemoryTables } from "./services/agentMemory.js";
import { startIndustryNewsScheduler } from "./services/industryNewsScheduler.js";

createApp().listen(config.PORT, () => {
  console.log(`Maejong intranet API listening on ${config.PORT}`);
  void ensureAgentMemoryTables()
    .then(() => {
      startIndustryNewsScheduler();
    })
    .catch((error) => {
      console.error("Failed to initialize agent memory tables.", error);
    });
});
