import fs from "node:fs";
import path from "node:path";
import { Config } from "@remotion/cli/config";

// The site's data bundle, built by `python3 scripts/build_site.py` (npm run data).
const BUNDLE = path.resolve(process.cwd(), "../site/assets/bundle.js");
const LOADER = path.resolve(process.cwd(), "scripts/puk-bundle-loader.cjs");

if (!fs.existsSync(BUNDLE)) {
  throw new Error(`Missing ${BUNDLE}. Run \`npm run data\` (python3 scripts/build_site.py) first.`);
}

Config.setVideoImageFormat("jpeg");
Config.setJpegQuality(95);
Config.setOverwriteOutput(true);
Config.setConcurrency(5);

Config.overrideWebpackConfig((config) => ({
  ...config,
  resolve: {
    ...config.resolve,
    alias: {
      ...(config.resolve?.alias as Record<string, string> | undefined),
      "puk-bundle$": BUNDLE,
    },
  },
  module: {
    ...config.module,
    rules: [
      ...(config.module?.rules ?? []),
      { test: BUNDLE, type: "javascript/auto", use: [{ loader: LOADER }] },
    ],
  },
}));
