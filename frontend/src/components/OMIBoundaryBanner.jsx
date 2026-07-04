export const OMI_BOUNDARY_COPY =
  'OMI stores review material only. Nothing becomes Memory/Canon until the owner explicitly confirms a separate apply-promotion step.';

export default function OMIBoundaryBanner() {
  return (
    <section
      className="omi-boundary-banner"
      data-testid="omi-boundary-banner"
      aria-label="OMI boundary"
    >
      <p>{OMI_BOUNDARY_COPY}</p>
    </section>
  );
}
