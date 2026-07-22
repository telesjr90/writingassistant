export default function OMIEmptyCandidateShellWarning({ children }) {
  return (
    <p
      className="omi-workflow-warning"
      data-testid="omi-empty-candidate-shell-warning"
    >
      {children}
    </p>
  );
}
