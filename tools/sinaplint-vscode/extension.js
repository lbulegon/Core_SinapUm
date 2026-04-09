/**
 * Extensão VS Code — SinapLint (relatório no painel de saída + diagnósticos simples).
 * Desenvolvimento: abrir esta pasta em VS Code e F5 (Launch Extension).
 */
const vscode = require("vscode");
const { execFile } = require("child_process");
const path = require("path");

const OUT = "SinapLint";

function getCoreRoot() {
  const cfg = vscode.workspace.getConfiguration("sinaplint");
  const custom = cfg.get("coreRoot");
  if (custom && String(custom).trim()) {
    return String(custom).trim();
  }
  const folders = vscode.workspace.workspaceFolders;
  if (!folders || !folders.length) {
    return "";
  }
  return folders[0].uri.fsPath;
}

function runSinapLint(output, coreRoot, pythonBin) {
  const script = path.join(coreRoot, "sinaplint.py");
  const proc = execFile(
    pythonBin,
    [script, "check", "--no-color"],
    { cwd: coreRoot, maxBuffer: 8 * 1024 * 1024 },
    (err, stdout, stderr) => {
      output.clear();
      output.appendLine(stdout || "");
      if (stderr) {
        output.appendLine(stderr);
      }
      if (err && err.code === 1) {
        vscode.window.showWarningMessage("SinapLint: score abaixo do limiar ou falha.");
      } else if (err) {
        vscode.window.showErrorMessage(`SinapLint: ${err.message}`);
      }
    }
  );
  return proc;
}

function activate(context) {
  const output = vscode.window.createOutputChannel(OUT);
  context.subscriptions.push(output);

  const disposableSave = vscode.workspace.onDidSaveTextDocument((doc) => {
    if (doc.languageId !== "python") {
      return;
    }
    const coreRoot = getCoreRoot();
    if (!coreRoot) {
      return;
    }
    const cfg = vscode.workspace.getConfiguration("sinaplint");
    const pythonBin = cfg.get("python") || "python3";
    runSinapLint(output, coreRoot, pythonBin);
  });

  const disposableCmd = vscode.commands.registerCommand("sinaplint.runCheck", () => {
    const coreRoot = getCoreRoot();
    if (!coreRoot) {
      vscode.window.showErrorMessage("SinapLint: defina workspace ou sinaplint.coreRoot.");
      return;
    }
    const cfg = vscode.workspace.getConfiguration("sinaplint");
    const pythonBin = cfg.get("python") || "python3";
    output.show(true);
    runSinapLint(output, coreRoot, pythonBin);
  });

  context.subscriptions.push(disposableSave, disposableCmd);
}

function deactivate() {}

module.exports = { activate, deactivate };
