interface Props {
  basenames: string[];
  onChange: (value: string) => void;
}

export function TextSelector(props: Props) {
  return (
    <span>
      <label htmlFor="text_select">Text:</label> &nbsp;
      <select id="text_select" onChange={(e) => props.onChange(e.target.value)}>
        {props.basenames.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </span>
  );
}
