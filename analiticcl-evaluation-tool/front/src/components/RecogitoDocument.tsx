import { Recogito } from "@recogito/recogito-js";
import "@recogito/recogito-js/dist/recogito.min.css";
import { useEffect, useState } from "react";
import type { Annotation, Doc } from "../App";
import { VOCABULARY } from "../App";
import GeotaggingWidget from "@recogito/geotagging-widget/src";

const htmlId = "text-content";

const gtw_config = {
  defaultOrigin: [ 48, 16 ]
};

interface Props {
  doc: Doc;
  updateAnnotations: (as: Annotation[]) => void;
}

export function RecogitoDocument(props: Props) {
  useRecogito(props, props.updateAnnotations);

  return (
    <div id={htmlId}>
      <div className="code">{props.doc.text}</div>
    </div>
  );
}

function useRecogito(props: Props, update: (as: Annotation[]) => void) {
  const [recogito, setRecogito] = useState<Recogito>(null);

  /**
   * Initialize Recogito and add listeners
   */
  useEffect(() => {
    const nextRecogito = initRecogito();

    const storeAnnotation = () => update(nextRecogito.getAnnotations());
    nextRecogito.on("createAnnotation", storeAnnotation);
    nextRecogito.on("deleteAnnotation", storeAnnotation);
    nextRecogito.on("updateAnnotation", storeAnnotation);

    setRecogito(nextRecogito);

    return () => nextRecogito.destroy();
  }, []);

  /**
   * Update annotations when recogito is loaded or props.docs changes
   */
  useEffect(() => {
    if (recogito == null || props.doc.id === "") return;
    recogito.setAnnotations(props.doc.annotations);
  }, [recogito, props.doc]);
}

const initRecogito = () =>
  new Recogito({
    content: htmlId,
    locale: "auto",
    mode: "pre",
    widgets: [
      { widget: "COMMENT" },
      {
        widget: "TAG",
        vocabulary: VOCABULARY,
      },
      { widget: GeotaggingWidget(gtw_config) }
    ],
    relationVocabulary: ["isRelated", "isPartOf", "isSameAs"],
    formatter: (annotation: any) => {
      // Get all tags in the bodies of the annotation
      const tags = annotation.bodies.flatMap((body: any) =>
        body.purpose === "tagging" ? body.value : []
      );

      // See CSS for the actual styling
      if (tags.length > 1) {
        return "tag-ambiguous";
      } else {
        const tag = tags[0];
        for (const vocab of VOCABULARY) {
          const label = vocab.label;
          if (tag === label) {
            return "tag-" + label;
          }
        }
      }
    },
  });
