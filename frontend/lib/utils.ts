const UNKNOWN_NAME = "Unknown reviewer";
const ANON_NAME = "Community critic";
const UNKNOWN_INITIALS = "??";

export function friendlyAuthorName(authorId: string | number | null | undefined): string {
  if (authorId === null || authorId === undefined) {
    return UNKNOWN_NAME;
  }

  if (typeof authorId === "number") {
    return authorId < 0 ? ANON_NAME : `User ${authorId}`;
  }

  const cleaned = authorId.trim();
  if (!cleaned) {
    return UNKNOWN_NAME;
  }

  if (cleaned.includes("@")) {
    const [local] = cleaned.split("@");
    return local || UNKNOWN_NAME;
  }

  if (/^[a-f0-9-]{16,}$/i.test(cleaned)) {
    return `User ${cleaned.slice(0, 6)}`;
  }

  return cleaned;
}

export function getInitials(authorId: string | number | null | undefined): string {
  if (authorId === null || authorId === undefined) {
    return UNKNOWN_INITIALS;
  }

  if (typeof authorId === "number") {
    return authorId < 0 ? "CC" : `U${authorId}`.slice(0, 3).toUpperCase();
  }

  const cleaned = authorId.trim();
  if (!cleaned) {
    return UNKNOWN_INITIALS;
  }

  const base = cleaned.includes("@") ? cleaned.split("@")[0] : cleaned;
  const tokens = base.replace(/[^\w\s-]/g, " ").split(/[\s_-]+/).filter(Boolean);
  const letterTokens = tokens
    .map((token) => token.replace(/[^a-zA-Z]/g, ""))
    .filter(Boolean);

  if (letterTokens.length >= 2) {
    return (letterTokens[0][0] + letterTokens[1][0]).toUpperCase();
  }

  if (letterTokens.length === 1) {
    const letters = letterTokens[0];
    if (letters.length >= 2) return letters.slice(0, 2).toUpperCase();
    return (letters + letters).slice(0, 2).toUpperCase();
  }

  const fallback = base.replace(/[^a-zA-Z]/g, "");
  if (fallback.length >= 2) return fallback.slice(0, 2).toUpperCase();
  if (fallback.length === 1) return (fallback + fallback).toUpperCase();

  return (base.slice(0, 2) || UNKNOWN_INITIALS).padEnd(2, "?").toUpperCase();
}

export function collapseWhitespace(text: string | null | undefined): string {
  if (!text) return "";
  return text.replace(/\s+/g, " ").trim();
}
