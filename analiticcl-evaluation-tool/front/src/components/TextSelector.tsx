import {Component} from "react";

class TextSelector extends Component<{ selection: string; basenames:string[]; onChange }> {
    render = () => {
      const options = this.props.basenames.map((option) => (
        <option key={option} value={option}>
          {option}
        </option>
      ));
      // options.unshift((<option disabled selected> -- select a text -- </option>));
      return (
        <span>
          Text: &nbsp;
          <select onChange={(e) => this.props.onChange(e.target.value)}>
            {options}
          </select>
        </span>
      );
    };
  }

export default TextSelector;