import path from "node:path";
import { fileURLToPath } from "node:url";

import { defineConfig } from "vite";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, "index.html"),
        ba: path.resolve(__dirname, "ba.html"),
        rs: path.resolve(__dirname, "rs.html"),
      },
    },
  },
});
