#!/usr/bin/env node
/**
 * Static contract & ES6 compatibility checker for Hose workflow JS code nodes.
 * Zero external dependencies — runs directly with Node.js.
 *
 * Usage:
 *   node scripts/check_node.mjs <code.js> [--strict-es6] [--vars <vars.json>]
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

/**
 * Strip comments and string/template literals so regex scans do not match
 * descriptive comments or literal text.
 */
function stripCommentsAndStrings(source) {
  let out = "";
  let i = 0;
  const len = source.length;
  let state = "normal"; // normal | sq | dq | bt | lineComment | blockComment

  while (i < len) {
    const ch = source[i];
    const next = source[i + 1];

    if (state === "normal") {
      if (ch === "/" && next === "/") {
        state = "lineComment";
        out += "  ";
        i += 2;
      } else if (ch === "/" && next === "*") {
        state = "blockComment";
        out += "  ";
        i += 2;
      } else if (ch === "'") {
        state = "sq";
        out += " ";
        i += 1;
      } else if (ch === '"') {
        state = "dq";
        out += " ";
        i += 1;
      } else if (ch === "`") {
        state = "bt";
        out += " ";
        i += 1;
      } else {
        out += ch;
        i += 1;
      }
    } else if (state === "lineComment") {
      if (ch === "\n") {
        state = "normal";
        out += "\n";
      } else {
        out += " ";
      }
      i += 1;
    } else if (state === "blockComment") {
      if (ch === "*" && next === "/") {
        state = "normal";
        out += "  ";
        i += 2;
      } else {
        out += ch === "\n" ? "\n" : " ";
        i += 1;
      }
    } else if (state === "sq" || state === "dq") {
      const quote = state === "sq" ? "'" : '"';
      if (ch === "\\") {
        out += "  ";
        i += 2;
      } else if (ch === quote) {
        state = "normal";
        out += " ";
        i += 1;
      } else {
        out += ch === "\n" ? "\n" : " ";
        i += 1;
      }
    } else if (state === "bt") {
      if (ch === "\\") {
        out += "  ";
        i += 2;
      } else if (ch === "`") {
        state = "normal";
        out += " ";
        i += 1;
      } else if (ch === "$" && next === "{") {
        // Keep interpolation expressions visible by replacing `${` with space
        out += "  ";
        i += 2;
      } else {
        out += ch === "\n" ? "\n" : " ";
        i += 1;
      }
    }
  }
  return out;
}

/**
 * Detect whether there is a `return` statement at top-level brace depth (0).
 */
function hasTopLevelReturn(stripped) {
  let depth = 0;
  const tokens = stripped.match(/[{}]|[A-Za-z_$][A-Za-z0-9_$]*/g) || [];
  for (const tok of tokens) {
    if (tok === "{") {
      depth += 1;
    } else if (tok === "}") {
      depth = Math.max(0, depth - 1);
    } else if (tok === "return" && depth === 0) {
      return true;
    }
  }
  return false;
}

function parseArgs(argv) {
  const opts = { codePath: "", strictEs6: false, varsPath: "" };
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === "--strict-es6") {
      opts.strictEs6 = true;
    } else if (arg === "--vars") {
      opts.varsPath = argv[++i] || "";
    } else if (!arg.startsWith("-") && !opts.codePath) {
      opts.codePath = arg;
    }
  }
  return opts;
}

function main() {
  const opts = parseArgs(process.argv.slice(2));
  if (!opts.codePath) {
    console.error("Usage: node check_node.mjs <code.js> [--strict-es6] [--vars <vars.json>]");
    process.exit(2);
  }

  const absCodePath = path.resolve(opts.codePath);
  if (!fs.existsSync(absCodePath)) {
    console.error(`❌ Code file not found: ${absCodePath}`);
    process.exit(1);
  }

  const code = fs.readFileSync(absCodePath, "utf8");
  const stripped = stripCommentsAndStrings(code);
  const errors = [];
  const warnings = [];

  if (!stripped.trim()) {
    errors.push("Code body is empty (only comments or whitespace).");
  }

  // 1. Check forbidden module/wrapper patterns
  if (/\bexport\s+(default|const|let|var|function|class|\{)/.test(stripped)) {
    errors.push("Forbidden 'export' statement found. Hose JS nodes must be an inline function body, not an ES module.");
  }
  if (/\bmodule\.exports\b|\bexports\./.test(stripped)) {
    errors.push("Forbidden CommonJS 'module.exports' / 'exports' found. Use 'return { ... }' instead.");
  }
  if (/^\s*import\s+[\w*{]/m.test(stripped)) {
    errors.push("Forbidden 'import' statement found. Cloud JS nodes run in an isolated sandbox without local file imports.");
  }
  if (/\brequire\s*\(/.test(stripped)) {
    warnings.push("Found 'require(...)'. Most Hose cloud JS sandboxes do not allow arbitrary CommonJS modules.");
  }
  if (/\bawait\b/.test(stripped) || /\basync\s+function\b/.test(stripped)) {
    errors.push("Found 'async/await'. Synchronous Hose JS node bodies execute via `return (function(__inj){ ... })` and do not await promises.");
  }

  // 2. Compile check inside a function body
  try {
    new Function(`"use strict";\n${code}`);
  } catch (err) {
    errors.push(`JavaScript syntax error inside function body: ${err.message}`);
  }

  // 3. Top-level return check
  if (!hasTopLevelReturn(stripped)) {
    errors.push("Missing top-level 'return { ... };' statement. Hose JS nodes must return a plain JS Object (Map).");
  }

  // 4. ES2020+ compatibility check
  const es2020Findings = [];
  if (/\?\./.test(stripped)) {
    es2020Findings.push("optional chaining '?.' (ES2020)");
  }
  if (/\?\?/.test(stripped)) {
    es2020Findings.push("nullish coalescing '??' (ES2020)");
  }
  if (/\.replaceAll\s*\(/.test(stripped)) {
    es2020Findings.push("String.prototype.replaceAll (ES2021)");
  }
  if (/\.at\s*\(/.test(stripped)) {
    es2020Findings.push("Array/String.prototype.at (ES2022)");
  }
  if (es2020Findings.length > 0) {
    const msg = `Uses post-ES6 syntax: ${es2020Findings.join(", ")}. Supported by newer sandboxes ('JS 节点（新）'), but may fail in strict ES6 engines.`;
    if (opts.strictEs6) {
      errors.push(`[--strict-es6] ${msg}`);
    } else {
      warnings.push(msg);
    }
  }

  // 5. Optional vars.json identifier validation
  if (opts.varsPath) {
    const absVarsPath = path.resolve(opts.varsPath);
    if (!fs.existsSync(absVarsPath)) {
      errors.push(`Vars file not found: ${absVarsPath}`);
    } else {
      try {
        const vars = JSON.parse(fs.readFileSync(absVarsPath, "utf8"));
        if (typeof vars !== "object" || vars === null || Array.isArray(vars)) {
          errors.push("vars.json must be a top-level JSON object mapping variable names to values.");
        } else {
          for (const key of Object.keys(vars)) {
            if (!VALID_IDENTIFIER.test(key) || RESERVED_WORDS.has(key)) {
              errors.push(`Invalid injected variable name "${key}": must be a legal JS identifier without spaces or reserved words.`);
            }
          }
        }
      } catch (err) {
        errors.push(`Failed to parse vars.json: ${err.message}`);
      }
    }
  }

  console.log(`Checking: ${absCodePath}`);
  for (const w of warnings) {
    console.warn(`⚠️  WARN: ${w}`);
  }
  for (const e of errors) {
    console.error(`❌ ERROR: ${e}`);
  }

  if (errors.length > 0) {
    process.exit(1);
  }
  console.log("✔ Passed Hose JS node static checks.");
}

main();
