#!/usr/bin/env node
"use strict";

const { spawnSync } = require("child_process");

function has(cmd) {
  const probe = spawnSync(cmd, ["--version"], { stdio: "ignore", shell: process.platform === "win32" });
  return !probe.error && probe.status === 0;
}

if (!has("ohnoo") && !has("ohnoo.exe")) {
  console.log(
    [
      "",
      "ohnoo installed the npm wrapper, but the Python CLI is not on your PATH yet.",
      "Finish setup with:",
      "",
      "  pip install ohnoo",
      "",
      "(or `pipx install ohnoo` to keep it isolated from your other Python packages)",
      "",
    ].join("\n")
  );
}
