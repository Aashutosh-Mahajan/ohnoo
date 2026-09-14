#!/usr/bin/env node
"use strict";

const { spawnSync } = require("child_process");

function findPythonOhnoo() {
  const candidates = ["ohnoo", "ohnoo.exe"];
  for (const cmd of candidates) {
    const probe = spawnSync(cmd, ["--version"], { stdio: "ignore", shell: process.platform === "win32" });
    if (!probe.error && probe.status === 0) return cmd;
  }
  return null;
}

function main() {
  const bin = findPythonOhnoo();
  if (!bin) {
    console.error(
      [
        "ohnoo: the Python CLI could not be found on your PATH.",
        "",
        "This npm package is a thin wrapper around the ohnoo Python package.",
        "Install it with one of:",
        "",
        "  pip install ohnoo",
        "  pipx install ohnoo",
        "",
        "Then re-run this command.",
      ].join("\n")
    );
    process.exit(1);
  }

  const args = process.argv.slice(2);
  const result = spawnSync(bin, args, { stdio: "inherit", shell: process.platform === "win32" });
  process.exit(result.status === null ? 1 : result.status);
}

main();
