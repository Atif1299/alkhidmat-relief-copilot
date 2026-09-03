"use client";

export type SopHit = {
  title?: string;
  category?: string;
  excerpt?: string;
  points?: string[];
  score?: number;
  source_file?: string;
  retrieval_mode?: string;
};

type ParsedSop = {
  title: string;
  category: string;
  keywords: string[];
  purpose: string;
  points: string[];
};

function stripInline(text: string): string {
  return text
    .replace(/\*\*([^*]+)\*\*/g, "$1")
    .replace(/\*([^*]+)\*/g, "$1")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/\s+/g, " ")
    .trim();
}

function looksLikeMarkdown(text: string): boolean {
  return /\*\*|##\s|^\s*\d+\.\s/m.test(text);
}

function parseExcerpt(raw: string): { category: string; keywords: string[]; purpose: string; points: string[] } {
  const spaced = raw
    .replace(/\r\n/g, "\n")
    .replace(/\s*##\s+/g, "\n## ")
    .replace(/\s*\*\*Category:\*\*/gi, "\n**Category:**")
    .replace(/\s*\*\*Keywords:\*\*/gi, "\n**Keywords:**");

  let category = "";
  let keywords: string[] = [];
  let purpose = "";
  let section = "";
  const points: string[] = [];

  for (const rawLine of spaced.split("\n")) {
    const line = rawLine.trim();
    if (!line || /^#\s/.test(line)) continue;
    if (/\*\*Category:\*\*/i.test(line)) {
      category = stripInline(line.split(/\*\*Category:\*\*/i)[1] || "");
      continue;
    }
    if (/\*\*Keywords:\*\*/i.test(line)) {
      keywords = stripInline(line.split(/\*\*Keywords:\*\*/i)[1] || "")
        .split(",")
        .map((k) => k.trim())
        .filter(Boolean);
      continue;
    }
    if (line.startsWith("## ")) {
      section = line.slice(3).trim().toLowerCase();
      continue;
    }
    const numbered = line.match(/^\d+\.\s+(.*)$/);
    if (numbered) {
      points.push(stripInline(numbered[1]));
      continue;
    }
    const text = stripInline(line);
    if (!text) continue;
    if (section === "purpose" && !purpose) {
      purpose = text;
    } else if (section === "rules" || section === "phrases") {
      points.push(text);
    } else if (!purpose && (section === "" || section === "purpose")) {
      purpose = text;
    } else if (section === "matching preference") {
      points.push(text);
    }
  }

  const uniqueKw = [...new Set(keywords.map((k) => k.toLowerCase()))].map(
    (k) => keywords.find((x) => x.toLowerCase() === k) || k
  );

  return { category, keywords: uniqueKw.slice(0, 8), purpose, points: points.slice(0, 6) };
}

function normalizeHit(hit: SopHit): ParsedSop {
  const storedPoints = (hit.points || []).map(stripInline).filter(Boolean);
  const excerpt = hit.excerpt || "";
  const parsed = excerpt && looksLikeMarkdown(excerpt) ? parseExcerpt(excerpt) : null;

  const purpose = parsed?.purpose || (!looksLikeMarkdown(excerpt) ? stripInline(excerpt) : "");
  const points = storedPoints.length ? storedPoints : parsed?.points || [];
  const category = hit.category || parsed?.category || "";
  const keywords = (parsed?.keywords || []).filter(
    (k) => k.toLowerCase() !== category.toLowerCase()
  );

  return {
    title: hit.title || "SOP",
    category,
    keywords,
    purpose,
    points,
  };
}

export function SopCitations({ hits }: { hits?: SopHit[] | null }) {
  if (!hits?.length) {
    return <p className="muted">No SOP citations for this case.</p>;
  }
  return (
    <ul className="citations">
      {hits.map((hit, i) => {
        const sop = normalizeHit(hit);
        return (
          <li key={`${sop.title}-${i}`} className="citation-card">
            <div className="citation-head">
              <strong>{sop.title}</strong>
              {sop.category ? <span className="badge ok">{sop.category}</span> : null}
            </div>
            {sop.keywords.length > 0 ? (
              <ul className="citation-kws">
                {sop.keywords.map((kw) => (
                  <li key={kw}>{kw}</li>
                ))}
              </ul>
            ) : null}
            {sop.purpose ? (
              <p className="citation-purpose">
                <span className="citation-label">Purpose</span>
                {sop.purpose}
              </p>
            ) : null}
            {sop.points.length > 0 ? (
              <div>
                <p className="citation-label" style={{ margin: "0.55rem 0 0.2rem" }}>
                  Rules
                </p>
                <ol className="citation-points">
                  {sop.points.map((point) => (
                    <li key={point}>{point}</li>
                  ))}
                </ol>
              </div>
            ) : null}
          </li>
        );
      })}
    </ul>
  );
}
