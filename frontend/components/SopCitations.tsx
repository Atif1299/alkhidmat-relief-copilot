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

export function SopCitations({ hits }: { hits?: SopHit[] | null }) {
  if (!hits?.length) {
    return <p className="muted">No SOP citations for this case.</p>;
  }
  return (
    <ul className="citations">
      {hits.map((hit, i) => (
        <li key={`${hit.title}-${i}`}>
          <strong>{hit.title}</strong>
          {hit.category ? <span className="muted"> · {hit.category}</span> : null}
          {hit.excerpt ? <p>{hit.excerpt}</p> : null}
          {hit.points && hit.points.length > 0 ? (
            <ol className="citation-points">
              {hit.points.map((point) => (
                <li key={point}>{point}</li>
              ))}
            </ol>
          ) : null}
        </li>
      ))}
    </ul>
  );
}
