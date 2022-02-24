import { Component } from "react";

// Annotation package
import { Recogito } from "@recogito/recogito-js";
import "@recogito/recogito-js/dist/recogito.min.css";

interface RecogitoDocumentProps {
  doc: any;
  setDoc: (doc: any) => void;
  vocabulary;
  // annotations: {}[];
  // setAnnotations: (annotations: {}[]) => void;
  // text: string;
  // setText: (text: string) => void;
}

const htmlId = "text-content"


class RecogitoDocument extends Component<RecogitoDocumentProps> {
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
      content: htmlId,
      locale: "auto",
      mode: "pre",
      widgets: [
        { widget: "COMMENT" },
        {
          widget: "TAG",
          vocabulary: this.props.vocabulary,
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
          for (const vocab of this.props.vocabulary) {
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
      <div id={htmlId}>
        <div className="code">{this.props.doc.text}</div>
      </div>
    );
  }
}

export default RecogitoDocument;
