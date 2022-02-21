import { Component } from "react";

class VersionSelector extends Component<{
  selection: string;
  annotation_versions: string[];
  onChange;
}> {
  
  shouldComponentUpdate = (newProps, _) => {
    return newProps.annotation_versions !== this.props.annotation_versions;
  };

  render = () => {
    const options = this.props.annotation_versions.map((option) => (
      <option key={option} value={option}>
        {option}
      </option>
    ));
    //     options.unshift((<option disabled selected> -- select a version -- </option>));
    return (
      <span>
        Version: &nbsp;
        <select onChange={(e) => this.props.onChange(e.target.value)}>
          {options}
        </select>
      </span>
    );
  };
}

export default VersionSelector;
