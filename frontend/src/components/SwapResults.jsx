// Card: Display Swap Suggestions
// Shows the ingredients the backend found and original → healthier replacement.

export default function SwapResults({ result }) {
  const { ingredients, suggestions, extracted_text } = result;

  return (
    <>
      <section className="card">
        <h2>2. Healthier swaps</h2>
        {suggestions.length === 0 ? (
          <p className="muted">
            No swaps found for these ingredients. Try a label with common items like sugar,
            palm oil, white flour or salt.
          </p>
        ) : (
          <ul className="swaps">
            {suggestions.map((swap) => (
              <li key={swap.original} className="swap">
                <div className="swap-line">
                  <span className="original">{swap.original}</span>
                  <span className="arrow">→</span>
                  <span className="replacement">{swap.replacement}</span>
                </div>
                <p className="reason">{swap.reason}</p>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="card">
        <h2>3. Ingredients found ({ingredients.length})</h2>
        {ingredients.length === 0 ? (
          <p className="muted">Text was found, but no ingredients could be separated out.</p>
        ) : (
          <ul className="chips">
            {ingredients.map((name) => (
              <li key={name}>{name}</li>
            ))}
          </ul>
        )}

        <details>
          <summary>Show raw OCR text</summary>
          <pre>{extracted_text}</pre>
        </details>
      </section>
    </>
  );
}
