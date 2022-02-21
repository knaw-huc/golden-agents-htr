import React, { useEffect, useState } from "react";

// Theming only
import "semantic-ui-css/semantic.min.css";
import { Container, Header, Segment } from "semantic-ui-react";

import PuffLoader from "react-spinners/PuffLoader";
import { css } from "@emotion/react";

import TextSelector from "./components/TextSelector";
import VersionSelector from "./components/VersionSelector";
import RecogitoDocument from "./components/RecogitoDocument";

const apiBase = "http://localhost:8000"; // development
// const apiBase = "/api"; // production; proxied to back-end in nginx.conf

const config: {} = require("./config.json");
const annotations0: {}[] = [];
const text0: string = "Please select a text (and version)";
const doc0 = { text: text0, annotations: annotations0 };

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
  { label: "location", uri: "http://vocab.getty.edu/aat/300008347" },
  { label: "room", uri: "http://vocab.getty.edu/aat/300008347" },

  { label: "category", uri: "http://vocab.getty.edu/aat/300008347" },
  { label: "quantifier", uri: "http://vocab.getty.edu/aat/300008347" },
];

const App = () => {
  const [baseNames, setBaseNames] = useState([]);
  const [doc, setDoc] = useState(doc0);
  const [annotationSelection, setAnnotationSelection] = useState("");
  const [annotationVersions, setAnnotationVersions] = useState([]);
  const [versionSelection, setVersionSelection] = useState("");
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
      console.error(res.status, res.statusText);
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
      // console.log("versionData=", versionData);
    } else {
      console.error(res.status, res.statusText);
    }
    return versionData;
  };

  const fetchBaseNames = async () => {
    const res = await fetch(apiBase + "/basenames", {
      headers: {
        "Content-Type": "text/json",
        Accept: "text/json",
      },
    });
    var baseNames = [];
    if (res.status >= 200 && res.status <= 299) {
      baseNames = await res.json();
      // console.log("baseNames=", baseNames);
    } else {
      console.log(res.status, res.statusText);
    }
    return baseNames;
  };

  useEffect(() => {
    setLoading(true);
    fetchVersionData().then((versionData) => {
      setAnnotationVersions(versionData);
    });
    fetchBaseNames().then((baseNames) => {
      setBaseNames(baseNames);
    });
    setLoading(false);
  }, []);

  useEffect(() => {
    setLoading(true);
    fetchPageData(baseNames[0], annotationVersions[0]).then((pageData) => {
      setDoc({ text: pageData.text, annotations: pageData.annotations });
    });
    setLoading(false);
  }, [annotationVersions, baseNames]);

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
    putAnnotations(newSelection, versionSelection, doc.annotations);
    setAnnotationSelection(newSelection);
    var newText;
    var newAnnotations;
    await fetchPageData(newSelection, versionSelection).then((pd) => {
      newText = pd.text;
      newAnnotations = pd.annotations;
    });
    setDoc({ text: newText, annotations: newAnnotations });
    setLoading(false);
  };

  const handleVersionSelectionChange = async (newVersionSelection: string) => {
    setLoading(true);
    putAnnotations(annotationSelection, newVersionSelection, doc.annotations);
    setVersionSelection(newVersionSelection);
    var newText;
    var newAnnotations;
    await fetchPageData(annotationSelection, newVersionSelection).then((pd) => {
      newText = pd.text;
      newAnnotations = pd.annotations;
    });
    setDoc({ text: newText, annotations: newAnnotations });
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
            basenames={baseNames}
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
          <RecogitoDocument doc={doc} setDoc={setDoc} vocabulary={VOCABULARY} />
        </Segment>
      </Container>
    </div>
  );
};

export default App;
