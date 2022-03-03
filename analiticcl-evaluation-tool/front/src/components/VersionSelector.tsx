interface Props {
  versions: string[];
  onChange: (value: string) => void;
}

export function VersionSelector(props: Props) {
  return (
    <span>
      <label htmlFor="version_select">Version:</label> &nbsp;
      <select
        id="version_select"
        onChange={(e) => props.onChange(e.target.value)}
      >
        {props.versions.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </span>
  );
}
