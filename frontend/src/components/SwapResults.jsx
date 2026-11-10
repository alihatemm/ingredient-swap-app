// Card: Display Swap Suggestions (#1206)
// A summary bar, each swap as "Instead of → Try", then every ingredient found
// (ones with a swap are highlighted) and the raw OCR text.

const LOW_CONFIDENCE = 70; // below this the photo was hard to read

function OcrSummary({ ingredients, suggestions, ocr, corrections }) {
  const details = [];
  if (ocr) {
    details.push(`read with "${ocr.method}" clean-up`);
    if (ocr.rotated) details.push(`turned ${ocr.rotated}°`);
    details.push(`${ocr.confidence}% OCR confidence`);
  }

  return (
    <section className="card summary">
      <div className="stats">
        <div className="stat">
          <span className="stat-number">{ingredients.length}</span>
          <span className="stat-label">ingredients found</span>
        </div>
        <div className="stat highlight">
          <span className="stat-number">{suggestions.length}</span>
          <span className="stat-label">healthier swaps</span>
        </div>
      </div>
      {details.length > 0 && <p className="muted small">Photo {details.join(" · ")}</p>}

      {ocr && ocr.confidence < LOW_CONFIDENCE && (
        <p className="warning">
          This photo was hard to read, so some ingredients may be missing or misspelled. A sharper, well-lit
          photo will give better results.
        </p>
      )}

      {corrections?.length > 0 && (
        <p className="muted small">
          Fixed OCR misreads:{" "}
          {corrections.map((c, i) => (
            <span key={c.from}>
              {i > 0 && ", "}
              <s>{c.from}</s> → {c.to}
            </span>
          ))}
        </p>
      )}
    </section>
  );
}

export default function SwapResults({ result }) {
  const { ingredients, suggestions, extracted_text, ocr, corrections } = result;
  const swapped = new Set(suggestions.map((swap) => swap.original));

  return (
    <>
      <OcrSummary ingredients={ingredients} suggestions={suggestions} ocr={ocr} corrections={corrections} />

      <section className="card">
        <h2>
          <span className="step">2</span> Healthier swaps
        </h2>
        {suggestions.length === 0 ? (
          <p className="muted">
            No swaps found for these ingredients. That can mean the product is already fairly simple, or that
            the photo was hard to read — check the ingredient list below.
          </p>
        ) : (
          <>
            <div className="swap-header" aria-hidden="true">
              <span>Instead of</span>
              <span />
              <span>Try</span>
            </div>
            <ul className="swaps">
              {suggestions.map((swap) => (
                <li key={swap.original} className="swap">
                  <div className="swap-line">
                    <span className="original" title="Original ingredient">
                      {swap.original}
                    </span>
                    <span className="arrow" aria-label="replace with">
                      →
                    </span>
                    <span className="replacement" title="Healthier replacement">
                      {swap.replacement}
                    </span>
                  </div>
                  <p className="reason">
                    {swap.category && <span className="badge">{swap.category}</span>}
                    {swap.reason}
                  </p>
                </li>
              ))}
            </ul>
          </>
        )}
      </section>

      <section className="card">
        <h2>
          <span className="step">3</span> Ingredients found
        </h2>
        {ingredients.length === 0 ? (
          <p className="muted">Text was found, but no ingredients could be separated out.</p>
        ) : (
          <>
            <ul className="chips">
              {ingredients.map((name) => (
                <li key={name} className={swapped.has(name) ? "has-swap" : ""}>
                  {name}
                </li>
              ))}
            </ul>
            <p className="legend muted small">
              <span className="legend-dot" /> has a healthier swap
            </p>
          </>
        )}

        <details>
          <summary>Show raw OCR text</summary>
          <pre>{extracted_text}</pre>
        </details>
      </section>
    </>
  );
}
