import React, { Component, useEffect, useState } from "react";

// Annotation package
import { Recogito } from "@recogito/recogito-js";
import "@recogito/recogito-js/dist/recogito.min.css";

// Theming only
import "semantic-ui-css/semantic.min.css";
import { Container, Header, Segment } from "semantic-ui-react";
// import { Container, Header, Segment, Button, Icon } from "semantic-ui-react";

import PuffLoader from "react-spinners/PuffLoader";
import { css } from "@emotion/react";

import TextSelector from "./components/TextSelector";

const apiBase = "http://localhost:8000"; // development
// const apiBase = "/api"; // production; proxied to back-end in nginx.conf

// interface Doc {
//   text: string;
//   annotations: {}[];
// };

interface DocumentProps {
  doc: any;
  setDoc: (doc: any) => void;
  // annotations: {}[];
  // setAnnotations: (annotations: {}[]) => void;
  // text: string;
  // setText: (text: string) => void;
}

const basenames: string[] = require("./ga-selection-basenames.json");
const defaultVersions: string[] = ["exp1", "exp2"];
const config: {} = require("./config.json");
const annotations0: {}[] = [];
const text0: string = "Please select a text (and version)";
const doc0 = { text: text0, annotations: annotations0 };

const useLocalStorageState = (key: string, defaultValue: string) => {
  const [state, setState] = useState(
    () => window.localStorage.getItem(key) || defaultValue
  );

  useEffect(() => {
    window.localStorage.setItem(key, state);
  }, [key, state]);

  return [state, setState];
};

// class TextSelector extends Component<{ selection: string; onChange }> {
//   render = () => {
//     const options = basenames.map((option) => (
//       <option key={option} value={option}>
//         {option}
//       </option>
//     ));
//     // options.unshift((<option disabled selected> -- select a text -- </option>));
//     return (
//       <span>
//         Text: &nbsp;
//         <select onChange={(e) => this.props.onChange(e.target.value)}>
//           {options}
//         </select>
//       </span>
//     );
//   };
// }

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

const VOCABULARY = [
  { label: "firstname", uri: "http://vocab.getty.edu/aat/300404651?" },
  { label: "familyname", uri: "http://vocab.getty.edu/aat/300008347?" },
  { label: "person", uri: "http://vocab.getty.edu/aat/300024979" },
  { label: "occupation", uri: "http://vocab.getty.edu/aat/300263369?" },

  { label: "material", uri: "http://vocab.getty.edu/aat/300010358" },
  { label: "property", uri: "http://vocab.getty.edu/aat/300008347" },
  { label: "object", uri: "http://vocab.getty.edu/aat/300311889" },
  { label: "picture", uri: "http://vocab.getty.edu/aat/300008347" },
  { label: "animal", uri: "http://vocab.getty.edu/aat/300008347" },

  { label: "currency", uri: "http://vocab.getty.edu/aat/300037316" },

  { label: "country", uri: "http://vocab.getty.edu/aat/300008347?" },
  { label: "region", uri: "http://vocab.getty.edu/aat/300182722?" },
  { label: "streetname", uri: "http://vocab.getty.edu/aat/300008347?" },
  //     { label: "location", uri: "http://vocab.getty.edu/aat/300008347" },
  { label: "room", uri: "http://vocab.getty.edu/aat/300008347" },

  { label: "category", uri: "http://vocab.getty.edu/aat/300008347" },
  { label: "quantifier", uri: "http://vocab.getty.edu/aat/300008347" },
];

// Make own component 'Document' for the annotatable source
class Document extends Component<DocumentProps> {
  htmlId = "text-content";
  r: Recogito; // the Recogito instance

  shouldComponentUpdate = (newProps, _) => {
    return newProps.doc !== this.props.doc;
  };

  componentDidUpdate = () => {
    // console.log('componentDidUpdate');
    // this.r.destroy();
    this.componentDidMount();
  };

  // Initialize the Recogito instance after the component is mounted in the page
  componentDidMount = () => {
    // console.debug("componentDidMount");
    this.r = new Recogito({
      content: this.htmlId,
      locale: "auto",
      mode: "pre",
      widgets: [
        { widget: "COMMENT" },
        {
          widget: "TAG",
          vocabulary: VOCABULARY,
        },
      ],
      relationVocabulary: ["isRelated", "isPartOf", "isSameAs"],
      formatter: (annotation: any) => {
        // Get all tags in the bodies of the annotation
        const tags = annotation.bodies.flatMap((body: any) =>
          body.purpose === "tagging" ? body.value : []
        );

        // See CSS for the actual styling
        const tagClasses: string[] = [];

        for (const tag of tags) {
          for (const vocab of VOCABULARY) {
            const label = vocab.label;
            if (tag === label) {
              tagClasses.push("tag-" + label);
            }
          }
        }

        return tagClasses.join(" ");
      },
    });

    const storeAnnotation = () => {
      let currentDoc = this.props.doc;
      currentDoc.annotations = this.r.getAnnotations();
      this.props.setDoc(currentDoc);
    };

    // Make sure that the annotations are stored in the state
    this.r.on("createAnnotation", storeAnnotation);
    this.r.on("deleteAnnotation", storeAnnotation);
    this.r.on("updateAnnotation", storeAnnotation);

    //     console.info(this.props);
    this.props.doc.annotations.map((annotation: {}) =>
      this.r.addAnnotation(annotation)
    );

    // For debugging, this can be helpful
    // console.log(r);
  };

  componentWillUnmount = () => {
    console.log("unmounting...");
    this.r.destroy();
  };

  render() {
    return (
      <div id={this.htmlId}>
        <div className="code">{this.props.doc.text}</div>
      </div>
    );
  }
}

const App = () => {
  const [doc, setDoc] = useState(doc0);
  const [annotationSelection, setAnnotationSelection] = useState(basenames[0]);
  const [annotationVersions, setAnnotationVersions] = useState(defaultVersions);
  const [versionSelection, setVersionSelection] = useState(
    annotationVersions.slice(-1)[0]
  );
  const [loading, setLoading] = useState(false);

  const fetchPageData = async (
    selectedAnnotation: string,
    selectedVersion: string
  ) => {
    const res = await fetch(
      apiBase + "/pagedata/" + selectedAnnotation + "/" + selectedVersion,
      {
        headers: {
          "Content-Type": "text/json",
          Accept: "text/json",
        },
      }
    );
    var data = { text: "", annotations: [] };
    if (res.status >= 200 && res.status <= 299) {
      data = await res.json();
    } else {
      console.log(res.status, res.statusText);
    }
    return data;
  };

  const fetchVersionData = async () => {
    const res = await fetch(apiBase + "/versions", {
      headers: {
        "Content-Type": "text/json",
        Accept: "text/json",
      },
    });
    var versionData = [];
    if (res.status >= 200 && res.status <= 299) {
      versionData = await res.json();
      console.log("versionData=", versionData);
    } else {
      console.log(res.status, res.statusText);
    }
    return versionData;
  };

  useEffect(() => {
    fetchVersionData().then((versionData) => {
      setAnnotationVersions(versionData);
    });
  }, []);

  const putAnnotations = (
    basename: string,
    version: string,
    annotations: {}[]
  ) => {
    console.debug(
      "TODO: PUT http://backend.com/documents/" +
        basename +
        "/" +
        version +
        "/annotations"
    );
    // console.info(annotations);
  };

  const handleAnnotationSelectionChange = async (newSelection: string) => {
    setLoading(true);
    putAnnotations(annotationSelection, versionSelection, doc.annotations);
    setAnnotationSelection(newSelection);
    var newText;
    var newAnnotations;
    await fetchPageData(newSelection, versionSelection).then((pd) => {
      newText = pd.text;
      newAnnotations = pd.annotations;
    });
    // await fetchText(newSelection).then(t => newText = t);
    // await fetchAnnotations(newSelection).then(a => newAnnotations = a);
    const newDoc = { text: newText, annotations: newAnnotations };

    setDoc(newDoc);
    setLoading(false);
  };

  const handleVersionSelectionChange = async (newVersionSelection) => {
    setLoading(true);
    putAnnotations(annotationSelection, newVersionSelection, doc.annotations);
    setVersionSelection(newVersionSelection);
    var newText;
    var newAnnotations;
    await fetchPageData(annotationSelection, newVersionSelection).then((pd) => {
      newText = pd.text;
      newAnnotations = pd.annotations;
    });
    // await fetchText(newSelection).then(t => newText = t);
    // await fetchAnnotations(newSelection).then(a => newAnnotations = a);
    const newDoc = { text: newText, annotations: newAnnotations };

    setDoc(newDoc);
    setLoading(false);
  };

  const color = "green";
  const override = css`
    margin: 0 auto;
    border-color: black;
  `;

  const version = config["version"];

  const legend = VOCABULARY.map((voc) => (
    <>
      <span className={"tag-" + voc.label}>{voc.label}</span>
      <span> | </span>
    </>
  ));

  return (
    <div className="App">
      <Container>
        <Header as="h1">
          Golden Agents: Annotation Evaluation ({version})
        </Header>

        <div>
          <TextSelector
            selection={annotationSelection}
            basenames={basenames}
            onChange={handleAnnotationSelectionChange}
          />
          &nbsp;
          <VersionSelector
            selection={versionSelection}
            annotation_versions={annotationVersions}
            onChange={handleVersionSelectionChange}
          />
          &nbsp;
          <PuffLoader
            color={color}
            css={override}
            loading={loading}
            size={20}
          />
        </div>

        <div>Tag Legend: | {legend}</div>

        {/*         <div>Akkoord: Jirsi <input type="checkbox"/> | Judith <input type="checkbox"/></div> */}

        <Segment>
          <Document doc={doc} setDoc={setDoc} />
        </Segment>
      </Container>
    </div>
  );
};

export default App;
