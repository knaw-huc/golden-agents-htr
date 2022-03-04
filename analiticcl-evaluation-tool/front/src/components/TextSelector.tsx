interface Props {
  basenames: string[];
  checks: {};
  onChange: (value: string) => void;
}

function checkbox(checks: {}, option: string, who: string) {
  var checked = false;
  if (Object.keys(checks).includes(option)) {
    if (Object.keys(checks[option]).includes(who)) {
      checked = checks[option][who];
    }
  }
  return checked ? "☑" : "☐";
}

export function TextSelector(props: Props) {
  return (
    <span>
      <label htmlFor="text_select">Text:</label> &nbsp;
      <select id="text_select" onChange={(e) => props.onChange(e.target.value)}>
        {props.basenames.map((option) => (
          <option key={option} value={option}>
            {checkbox(props.checks, option, "jirsi")}{" "}
            {checkbox(props.checks, option, "judith")} {option}
          </option>
        ))}
      </select>
    </span>
  );
}
