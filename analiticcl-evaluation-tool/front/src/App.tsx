import React, { useEffect, useState, useCallback } from "react";

// Theming only
import "semantic-ui-css/semantic.min.css";
import {
  Container,
  Header,
  Segment,
  Button,
  Dimmer,
  Loader,
} from "semantic-ui-react";

// import { css } from "@emotion/react";

import { TextSelector } from "./components/TextSelector";
import { VersionSelector } from "./components/VersionSelector";
import { RecogitoDocument } from "./components/RecogitoDocument";

interface AnnotationBody {
  type: string;
  purpose?: string;
  value: any;
  modified?: string;
}

interface AnnotationSelector {
  type: string;
  start?: number;
  end?: number;
  exact?: string;
}

export interface Annotation {
  "@context": string[];
  body: AnnotationBody[];
  generated: string;
  generator: { id: string; type: string; name: string };
  id: string;
  motivation: string;
  target: { source: string; selector: AnnotationSelector[] };
  type: string;
}

export interface Doc {
  id: string;
  version: string;
  text: string;
  annotations: Annotation[];
  transkribusURL: string;
  acceptedByJirsi: boolean;
  acceptedByJudith: boolean;
  acceptedByHarm: boolean;
}

interface InitData {
  baseNames: string[];
  annotationVersions: string[];
}

const config: {} = require("./config.json");
const version = config["version"];
const inDevelopmentMode = config["developmentMode"];
const versionSelector = config["versionSelector"]; //show version menu?
const apiBase = inDevelopmentMode ? "http://localhost:8000" : "/api"; // production; proxied to back-end in nginx.conf

const annotations0: Annotation[] = [];
const text0: string = "Please select a text (and version)";
const doc0: Doc = {
  id: "",
  version: "",
  text: text0,
  annotations: annotations0,
  transkribusURL: "",
  acceptedByHarm: false,
  acceptedByJirsi: false,
  acceptedByJudith: false,
};

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
  var data = { text: "", annotations: [], transkribus_url: "" };
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

const putAnnotations = async (doc: Doc) => {
  if (doc.annotations.length === 0) {
    return;
  }
  const requestOptions = {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      annotations: doc.annotations,
      checked: {
        harm: doc.acceptedByHarm,
        jirsi: doc.acceptedByJirsi,
        judith: doc.acceptedByJudith,
      },
    }),
  };
  const url = `${apiBase}/annotations/${doc.id}/${doc.version}`;
  console.log(url);
  await fetch(url, requestOptions);
};

const fetchChecks = async () => {
  const res = await fetch(apiBase + "/checks", {
    headers: {
      "Content-Type": "text/json",
      Accept: "text/json",
    },
  });
  var checks = {};
  if (res.status >= 200 && res.status <= 299) {
    checks = await res.json();
    // console.log("versionData=", versionData);
  } else {
    console.error(res.status, res.statusText);
  }
  return checks;
};

export const VOCABULARY = [
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

// const color = "green";
// const override = css`
//   margin: 0 auto;
//   border-color: black;
// `;

const legend = VOCABULARY.map((voc) => (
  <span key={voc.label}>
    <span className={"tag-" + voc.label}>{voc.label}</span>
    <span> | </span>
  </span>
));

const App = () => {
  const [initData, setInitData] = useState<InitData>({
    baseNames: [],
    annotationVersions: [],
  });
  const [doc, setDoc] = useState(doc0);
  const [loading, setLoading] = useState(false);
  const [checks, setChecks] = useState({});

  useEffect(() => {
    setLoading(true);

    Promise.all([fetchVersionData(), fetchBaseNames(), fetchChecks()]).then(
      ([versions, ids, _checks]) => {
        setChecks(_checks);
        fetchPageData(ids[0], versions[0]).then(
          (pageData: Pick<Doc, "annotations" | "text">) => {
            const _doc: Doc = {
              id: ids[0],
              version: versions[0],
              transkribusURL: pageData["transkribus_url"],
              acceptedByHarm: pageData["checked"]["harm"],
              acceptedByJirsi: pageData["checked"]["jirsi"],
              acceptedByJudith: pageData["checked"]["judith"],
              ...pageData,
            };
            setDoc(_doc);
            setInitData({ annotationVersions: versions, baseNames: ids });
            setLoading(false);
          }
        );
      }
    );
  }, []);

  const handleTextChange = useCallback(
    (id: Doc["id"]) => {
      setLoading(true);

      fetchPageData(id, doc.version).then((pd) => {
        setDoc({
          id,
          version: doc.version,
          text: pd.text,
          annotations: pd.annotations,
          transkribusURL: pd.transkribus_url,
          acceptedByHarm: pd["checked"]["harm"],
          acceptedByJirsi: pd["checked"]["jirsi"],
          acceptedByJudith: pd["checked"]["judith"],
        });
        setLoading(false);
        // console.log(doc);
      });
    },
    [doc]
  );

  const handleVersionChange = useCallback(
    (version: Doc["version"]) => {
      setLoading(true);

      fetchPageData(doc.id, version).then((pd) => {
        setDoc({
          id: doc.id,
          version,
          text: pd.text,
          annotations: pd.annotations,
          transkribusURL: pd.transkribus_url,
          acceptedByHarm: pd["checked"]["harm"],
          acceptedByJirsi: pd["checked"]["jirsi"],
          acceptedByJudith: pd["checked"]["judith"],
        });
        setLoading(false);
      });
    },
    [doc]
  );

  const Checked = () => {
    return (
      <>
        Checked: <label htmlFor="harm_checkbox">Harm</label>{" "}
        <input
          type="checkbox"
          id="harm_checkbox"
          defaultChecked={doc.acceptedByHarm}
          onChange={(e) => {
            doc.acceptedByHarm = !doc.acceptedByHarm;
            setDoc(doc);
          }}
        />{" "}
        <label htmlFor="jirsi_checkbox">Jirsi</label>{" "}
        <input
          type="checkbox"
          id="jirsi_checkbox"
          defaultChecked={doc.acceptedByJirsi}
          onChange={(e) => {
            doc.acceptedByJirsi = !doc.acceptedByJirsi;
            setDoc(doc);
          }}
        />{" "}
        | <label htmlFor="judith_checkbox">Judith</label>{" "}
        <input
          type="checkbox"
          id="judith_checkbox"
          defaultChecked={doc.acceptedByJudith}
          onChange={(e) => {
            doc.acceptedByJudith = !doc.acceptedByJudith;
            setDoc(doc);
          }}
        />
      </>
    );
  };

  const SaveButton = () => {
    const handleClick = () => {
      putAnnotations(doc).then(() => fetchChecks().then((c) => setChecks(c)));
    };
    return (
      <>
        <Button primary icon compact onClick={handleClick}>
          Save annotations
        </Button>
      </>
    );
  };

  // const DownloadButton = () => {
  //   const handleClick = () => {
  //     putAnnotations(doc);
  //   };
  //   return (
  //     <div>
  //       <Button primary icon className="downloadbutton" onClick={handleClick}>
  //         <a
  //           href={`data:text/json;charset=utf-8,${encodeURIComponent(
  //             JSON.stringify(doc.annotations, null, 2)
  //           )}`}
  //           download={`${doc.id}.json`}
  //         >
  //           {`Download Json`}
  //         </a>{" "}
  //         <Icon name="download" />
  //       </Button>
  //     </div>
  //   );
  // };

  return (
    <div className="App">
      <Container>
        <Header as="h1">
          Golden Agents: Annotation Evaluation (v{version})
          <small>
            <a
              href={apiBase + "/html/instructions.html"}
              target="_blank"
              rel="noreferrer"
            >
              {" "}
              (?)
            </a>
          </small>
        </Header>

        <Segment>
          <div>
            <TextSelector
              basenames={initData.baseNames}
              checks={checks}
              onChange={handleTextChange}
            />
            {versionSelector ? (
              <>
                &nbsp;|&nbsp;
                <VersionSelector
                  versions={initData.annotationVersions}
                  onChange={handleVersionChange}
                />
              </>
            ) : (
              ""
            )}
            &nbsp;|&nbsp;
            <Checked />
            &nbsp;|&nbsp;
            <SaveButton />
          </div>
        </Segment>

        <Segment>
          <div>
            Tag Legend: | <span className="tag-ambiguous">(ambiguous)</span> |{" "}
            {legend}
          </div>
        </Segment>

        <Segment>
          <a href={doc.transkribusURL} target="_blank" rel="noreferrer">
            Page in Stadsarchief
          </a>
        </Segment>

        <Segment>
          <Dimmer active={loading}>
            <Loader>
              Loading text {doc.id}.{doc.version} ...
            </Loader>
          </Dimmer>
          <RecogitoDocument
            doc={doc}
            updateAnnotations={(annotations: Annotation[]) =>
              setDoc((d) => ({ ...d, annotations }))
            }
          />
        </Segment>
      </Container>
    </div>
  );
};

export default App;
