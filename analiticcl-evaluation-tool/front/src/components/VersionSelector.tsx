interface Props {
  versions: string[]
  onChange: (value: string) => void
}
  
export function VersionSelector(props: Props) {
  return (
    <span>
      Version: &nbsp;
      <select onChange={(e) => props.onChange(e.target.value)}>
        {
          props.versions.map(option =>
            <option key={option} value={option}>
              {option}
            </option>
          )
        }
      </select>
    </span>
  )
}
