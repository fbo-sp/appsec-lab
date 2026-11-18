/** Cores do editor no modo escuro (ADR-026): fundo e sintaxe pensados para fundo escuro. */
import { HighlightStyle, syntaxHighlighting } from "@codemirror/language";
import type { Extension } from "@codemirror/state";
import { EditorView } from "@codemirror/view";
import { tags as t } from "@lezer/highlight";

const escuroBase = EditorView.theme(
  {
    "&": { color: "#d7dbe3", backgroundColor: "#161a22" },
    ".cm-content": { caretColor: "#e6e9ef" },
    ".cm-cursor, .cm-dropCursor": { borderLeftColor: "#e6e9ef" },
    "&.cm-focused .cm-selectionBackground, .cm-selectionBackground, .cm-content ::selection": {
      backgroundColor: "#2f3d5c",
    },
    ".cm-gutters": { backgroundColor: "#161a22", color: "#5a6375", border: "none" },
    ".cm-activeLine": { backgroundColor: "#1c2130" },
    ".cm-activeLineGutter": { backgroundColor: "#1c2130", color: "#9aa3b2" },
    ".cm-matchingBracket, .cm-nonmatchingBracket": { backgroundColor: "#2c3447", outline: "1px solid #46516b" },
    ".cm-searchMatch": { backgroundColor: "#4a3f1a" },
    ".cm-panels": { backgroundColor: "#1b2029", color: "#d7dbe3" },
    ".cm-tooltip": { backgroundColor: "#1b2029", border: "1px solid #2c3340", color: "#d7dbe3" },
  },
  { dark: true },
);

const escuroSintaxe = HighlightStyle.define([
  { tag: [t.keyword, t.controlKeyword, t.operatorKeyword, t.definitionKeyword, t.moduleKeyword], color: "#c792ea" },
  { tag: [t.string, t.special(t.string), t.regexp], color: "#c3e88d" },
  { tag: [t.comment, t.lineComment, t.blockComment, t.docComment], color: "#6b7489", fontStyle: "italic" },
  { tag: [t.function(t.variableName), t.function(t.definition(t.variableName)), t.definition(t.className)], color: "#82aaff" },
  { tag: [t.className, t.typeName, t.standard(t.variableName)], color: "#ffcb6b" },
  { tag: [t.number, t.bool, t.null, t.atom], color: "#f78c6c" },
  { tag: [t.propertyName, t.attributeName], color: "#89ddff" },
  { tag: [t.tagName, t.angleBracket], color: "#f07178" },
  { tag: [t.operator, t.punctuation, t.bracket], color: "#a6b0c3" },
  { tag: t.invalid, color: "#f0766b" },
]);

export const temaEditorEscuro: Extension = [escuroBase, syntaxHighlighting(escuroSintaxe)];
