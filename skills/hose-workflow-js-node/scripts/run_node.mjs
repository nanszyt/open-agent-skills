#!/usr/bin/env node
/**
 * Local Hose workflow JS node sandbox simulator.
 * Simulates Hose cloud execution (`const <var> = __inj["<var>"]; ...`) using Node.js.
 * Zero external dependencies.
 *
 * Usage:
 *   node scripts/run_node.mjs --code <code.js> [--vars <vars.json>] [--out <result.json>] [--no-write]
 */

import fs from "node:fs";
import path from "node:path";

const RESERVED_WORDS = new Set([
  "break", "case", "catch", "class", "const", "continue", "debugger",
  "default", "delete", "do", "else", "enum", "export", "extends", "false",
  "finally", "for", "function", "if", "import", "in", "instanceof", "new",
  "null", "return", "super", "switch", "this", "throw", "true", "try",
  "typeof", "var", "void", "while", "with", "yield", "let", "static",
  "implements", "interface", "package", "private", "protected", "public",
  "await"
]);

const VALID_IDENTIFIER = /^[A-Za-z_$\u00A0-\uFFFF][A-Za-z0-9_$\u00A0-\uFFFF]*$/;

function parseArgs(argv) {
  const opts = { codePath: "", varsPath: "", outPath: "", writeFile: true };
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === "--code" || arg === "-c") {
      opts.codePath = argv[++i] || "";
    } else if (arg === "--vars" || arg === "-v") {
      opts.varsPath = argv[++i] || "";
    } else if (arg === "--out" || arg === "-o") {
      opts.outPath = argv[++i] || "";
    } else if (arg === "--no-write") {
      opts.writeFile = false;
    } else if (!arg.startsWith("-") && !opts.codePath) {
      opts.codePath = arg;
    }
  }
  return opts;
}

function indent(text, spaces) {
  const prefix = " ".repeat(spaces);
  return text
    .split("\n")
    .map(line => (line ? prefix + line : ""))
    .join("\n");
}

function executeInlineCode(code, vars) {
  const keys = Object.keys(vars);
  for (const name of keys) {
    if (!VALID_IDENTIFIER.test(name) || RESERVED_WORDS.has(name)) {
      throw new Error(
        `Injected variable "${name}" is not a valid JS identifier (remove spaces/special characters or rename in Hose node input mapping).`
      );
    }
  }

  const bindings = keys
    .map(name => `const ${name} = __inj[${JSON.stringify(name)}];`)
    .join("\n");

  const wrapped = `"use strict";
return (function(__inj) {
${indent(bindings, 2)}
${indent(code, 2)}
});`;

  return new Function(wrapped)()(vars);
}

function main() {
  const opts = parseArgs(process.argv.slice(2));
  if (!opts.codePath) {
    console.error("Usage: node run_node.mjs --code <code.js> [--vars <vars.json>] [--out <result.json>] [--no-write]");
    process.exit(2);
  }

  const absCodePath = path.resolve(opts.codePath);
  if (!fs.existsSync(absCodePath)) {
    console.error(`❌ Code file not found: ${absCodePath}`);
    process.exit(1);
  }

  let vars = {};
  if (opts.varsPath) {
    const absVarsPath = path.resolve(opts.varsPath);
    if (!fs.existsSync(absVarsPath)) {
      console.error(`❌ Vars file not found: ${absVarsPath}`);
      process.exit(1);
    }
    vars = JSON.parse(fs.readFileSync(absVarsPath, "utf8"));
    if (typeof vars !== "object" || vars === null || Array.isArray(vars)) {
      console.error("❌ vars.json must be a top-level JSON object.");
      process.exit(1);
    }
  }

  const code = fs.readFileSync(absCodePath, "utf8");
  let result;
  try {
    result = executeInlineCode(code, vars);
  } catch (err) {
    console.error(`❌ Execution failed: ${err.message}`);
    process.exit(1);
  }

  if (typeof result !== "object" || result === null || Array.isArray(result)) {
    console.error(
      `❌ Contract violation: Hose JS node must return a plain JS Object (Map), got ${
        Array.isArray(result) ? "Array" : result === null ? "null" : typeof result
      }.`
    );
    process.exit(1);
  }

  const formatted = JSON.stringify(result, null, 2);
  if (opts.writeFile) {
    const outPath = opts.outPath
      ? path.resolve(opts.outPath)
      : absCodePath.replace(/\.(js|mjs|ts)$/i, ".result.json");
    fs.writeFileSync(outPath, formatted + "\n", "utf8");
    console.log(`📄 Result saved: ${outPath}`);
  }
  console.log(formatted);
}

main();
