import React, { Component, useState } from "react";

// Annotation package
import { Recogito } from "@recogito/recogito-js";
import "@recogito/recogito-js/dist/recogito.min.css";

// Theming only
import "semantic-ui-css/semantic.min.css";
import { Container, Header, Segment } from "semantic-ui-react";
// import { Container, Header, Segment, Button, Icon } from "semantic-ui-react";

import PuffLoader from "react-spinners/PuffLoader";
import { css } from "@emotion/react";

const apiBase = "http://localhost:2081"; // development
// const apiBase = "/api"; // production

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
const annotations0:{}[] = [];
const text0: string = 'Please select a text';
const doc0={text:text0,annotations:annotations0};

class TextSelector extends Component<{selection:string, onChange}> {

  render = () => {
    const options = basenames.map(option => (
      <option key={option} value={option}>
        {option}
      </option>
    ));
    options.unshift((<option disabled selected> -- select a text -- </option>));
    return (
      <span>
      Text: &nbsp;
      <select onChange = { (e) => this.props.onChange(e.target.value) }>
        {options}
      </select>
      </span>
    )
  }
}

const VOCABULARY = [
    { label: "firstname", uri: "http://vocab.getty.edu/aat/300008347?" },
    { label: "familyname", uri: "http://vocab.getty.edu/aat/300008347?" },
    { label: "person",   uri: "http://vocab.getty.edu/aat/300024979" },
    { label: "occupation", uri: "http://vocab.getty.edu/aat/300008347?" },

    { label: "material", uri: "http://vocab.getty.edu/aat/300010358" },
    { label: "property", uri: "http://vocab.getty.edu/aat/300008347" },
    { label: "object",   uri: "http://vocab.getty.edu/aat/300311889" },
    { label: "picture", uri: "http://vocab.getty.edu/aat/300008347" },

    { label: "currency", uri: "http://vocab.getty.edu/aat/300008347" },

    { label: "streetname", uri: "http://vocab.getty.edu/aat/300008347?" },
//     { label: "location", uri: "http://vocab.getty.edu/aat/300008347" },
    { label: "room", uri: "http://vocab.getty.edu/aat/300008347" },

    { label: "category", uri: "http://vocab.getty.edu/aat/300008347" },
  ];

// Make own component 'Document' for the annotatable source
class Document extends Component<DocumentProps> {
  htmlId = "text-content";
  r; // the Recogito instance


  shouldComponentUpdate = (newProps,_) => {
    return newProps.doc !== this.props.doc;
  }

  componentDidUpdate = () => {
    // console.log('componentDidUpdate');
    // this.r.destroy();
    this.componentDidMount();
  }

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
                    tagClasses.push("tag-"+label);
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

    console.info(this.props);
    this.props.doc.annotations.map((annotation: {}) => this.r.addAnnotation(annotation));

    // For debugging, this can be helpful
    // console.log(r);
  }

  componentWillUnmount = () => {
    console.log('unmounting...');
    this.r.destroy();
  }

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
  const [selection, setSelection] = useState(basenames[0]);
  const [loading, setLoading] = useState(false);

  const fetchPageData = async (selected:string) => {
    const res = await fetch(apiBase + "/pagedata/" + selected, {
      headers: {
        "Content-Type": "text/json",
        Accept: "text/json",
      },
    });
    const data = await res.json();
    return data;
  }

//   const fetchBaseNames = async () => {
//     return await fetch(apiBase + "/basenames")
//       .then(res => res.json());
//   }

  // const fetchText = async (selected:string) => {
  //   const res = await fetch(selected+".txt", {
  //     headers: {
  //       "Content-Type": "text/plain",
  //       Accept: "text/plain",
  //     },
  //   });
  //   const text = await res.text();
  //   return text;
  // }

  // const fetchAnnotations = async (selected:string) => {
  //   const res = await fetch(selected+".json", {
  //     headers: {
  //       "Content-Type": "application/json",
  //       Accept: "application/json",
  //     },
  //   });
  //   const annotations = await res.json();
  //   return annotations;
  // }

  const putAnnotations = (basename:string, annotations:{}[]) => {
    console.debug("TODO: PUT http://backend.com/documents/"+basename+"/annotations");
    console.info(annotations);
  }

  const handleSelectionChange = async (newSelection) => {
    setLoading(true);
    putAnnotations(selection,doc.annotations);
    setSelection(newSelection);
    var newText;
    var newAnnotations;
    await fetchPageData(newSelection).then(pd => {newText = pd.text; newAnnotations=pd.annotations});
    // await fetchText(newSelection).then(t => newText = t);
    // await fetchAnnotations(newSelection).then(a => newAnnotations = a);
    const newDoc = {text:newText,annotations:newAnnotations};

    setDoc(newDoc);
    setLoading(false);
  }

  const color = "green";
  const override = css`
    margin: 0 auto;
    border-color: black;
  `;

  const dateTime = new Date();
  const version = "v"+dateTime.getFullYear()+"-"+(dateTime.getMonth()+1)+"-"+dateTime.getDate();

  const legend = VOCABULARY.map(voc => (
         <><span className={"tag-"+voc.label}>{voc.label}</span><span> | </span></>
        ));

  return (
    <div className="App">
      <Container>
        <Header as="h1">Golden Agents: Annotation Evaluation ({version})</Header>

        <div>
          <TextSelector selection={selection} onChange={handleSelectionChange}/>
          &nbsp;
          <PuffLoader color={color} css={override} loading={loading} size={20} />
        </div>

        <div>Tag Legend: | {legend}</div>

        <Segment>
          <Document doc={doc} setDoc={setDoc} />
        </Segment>
      </Container>
    </div>
  );
};

export default App;