// Webpack loader (and plain Node helper) for ../site/assets/bundle.js.
// The site bundle is `window.PUK = {...};`. This strips the prefix, checks the
// JSON parses, and hands it to the video as an ES module default export, so
// every figure on screen is read from the same data the site shows.
"use strict";

function parsePukBundle(source) {
  const start = source.indexOf("{");
  if (!source.trimStart().startsWith("window.PUK") || start < 0) {
    throw new Error("bundle.js does not start with `window.PUK = {`; rebuild it with python3 scripts/build_site.py");
  }
  const json = source.slice(start).trim().replace(/;\s*$/, "");
  return JSON.parse(json);
}

function pukBundleLoader(source) {
  const data = parsePukBundle(source);
  return `export default ${JSON.stringify(data)};`;
}

module.exports = pukBundleLoader;
module.exports.parsePukBundle = parsePukBundle;
