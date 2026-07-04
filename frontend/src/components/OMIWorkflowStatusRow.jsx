export default function OMIWorkflowStatusRow({ row }) {
  return (
    <tr>
      <th scope="row">{row.area}</th>
      <td>{row.count}</td>
      <td>
        <span className={`omi-status-badge ${row.statusTone ?? ''}`.trim()}>
          {row.status}
        </span>
      </td>
      <td>{row.blockers}</td>
      <td>{row.evidence}</td>
      <td>
        <button
          className="secondary-button omi-row-action"
          type="button"
          aria-label={`${row.action} for ${row.area}`}
          onClick={row.onAction}
        >
          {row.action}
        </button>
      </td>
      <td>{row.disabledReason}</td>
    </tr>
  );
}
