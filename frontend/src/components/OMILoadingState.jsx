export default function OMILoadingState({ children }) {
  return (
    <p className="omi-loading-state" role="status">
      {children}
    </p>
  );
}
