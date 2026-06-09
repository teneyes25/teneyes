import { createApp } from "./app.js";
import { config } from "./config.js";
import { startIndustryNewsScheduler } from "./services/industryNewsScheduler.js";

createApp().listen(config.PORT, () => {
  console.log(`Maejong intranet API listening on ${config.PORT}`);
  startIndustryNewsScheduler();
});
