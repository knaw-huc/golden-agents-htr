import React, { useEffect, useState, useCallback } from "react";

// Theming only
import "semantic-ui-css/semantic.min.css";
import { Container, Header, Segment } from "semantic-ui-react";

import PuffLoader from "react-spinners/PuffLoader";
import { css } from "@emotion/react";

import { TextSelector } from "./components/TextSelector";
import { VersionSelector } from "./components/VersionSelector";
import RecogitoDocument from "./components/RecogitoDocument";

const apiBase = "http://localhost:8000"; // development
// const apiBase = "/api"; // production; proxied to back-end in nginx.conf

const config: {} = require("./config.json");
const version = config["version"];

const annotations0: Annotation[] = [];
const text0: string = "Please select a text (and version)";
const doc0: Doc = { id: '', version: '', text: text0, annotations: annotations0 };

interface AnnotationBody {
  type: string
  purpose?: string
  value: any
  modified?: string
}

interface AnnotationSelector {
  type: string
  start?: number
  end?: number
  exact?: string
}

interface Annotation {
  "@context": string[]
  body: AnnotationBody[]
  generated: string
  generator: { id: string, type: string, name: string }
  id: string
  motivation: string
  target: { source: string, selector: AnnotationSelector[] }
  type: string
}

interface Doc {
  id: string,
  version: string
  text: string
  annotations: Annotation[]
}

interface InitData {
  baseNames: string[]
  annotationVersions: string[]
}

const fetchPageData = async (
  selectedAnnotation: string,
  selectedVersion: string
) => {
  const res = await fetch(
    `${apiBase}/pagedata/${selectedAnnotation}/${selectedVersion}`,
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

const color = "green";
const override = css`
  margin: 0 auto;
  border-color: black;
`;

const legend = VOCABULARY.map((voc) => (
  <span key={voc.label}>
    <span className={"tag-" + voc.label}>{voc.label}</span>
    <span> | </span>
  </span>
));

const App = () => {
  const [initData, setInitData] = useState<InitData>({ baseNames: [], annotationVersions: [] })
  const [doc, setDoc] = useState(doc0);

  // const [annotationSelection, setAnnotationSelection] = useState("");
  // const [versionSelection, setVersionSelection] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true)

    Promise
      .all([fetchVersionData(), fetchBaseNames()])
      .then(([versions, ids]) => {
        fetchPageData(ids[0], versions[0])
          .then((pageData: Pick<Doc, 'annotations' | 'text'>) => {
            const doc: Doc = { id: ids[0], version: versions[0], ...pageData }
            setDoc(doc)
            setInitData({ annotationVersions: versions, baseNames: ids })
            setLoading(false);
          });
      })
  }, []);

  const handleAnnotationSelectionChange = useCallback((id: Doc['id']) => {
    setLoading(true)

    putAnnotations(id, doc.version, doc.annotations)

    fetchPageData(id, doc.version)
      .then((pd) => {
        setDoc({ id, version: doc.version, text: pd.text, annotations: pd.annotations })
        setLoading(false)
      })
  }, [doc])

  const handleVersionSelectionChange = useCallback((version: Doc['version']) => {
    setLoading(true)

    putAnnotations(doc.id, version, doc.annotations)

    fetchPageData(doc.id, version)
      .then((pd) => {
        setDoc({ id: doc.id, version, text: pd.text, annotations: pd.annotations })
        setLoading(false)
      })
  }, [doc])

  console.log("LOADING APP")

  return (
    <div className="App">
      <Container>
        <Header as="h1">
          Golden Agents: Annotation Evaluation ({version})
        </Header>

        <div>
          <TextSelector
            basenames={initData.baseNames}
            onChange={handleAnnotationSelectionChange}
          />
          &nbsp;
          <VersionSelector
            versions={initData.annotationVersions}
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
