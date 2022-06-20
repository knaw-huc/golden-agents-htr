analiticcl_presentation.pdf: analiticcl_presentation.md
	pandoc -t beamer analiticcl_presentation.md -o analiticcl_presentation.pdf

boedelverwerking_pres.pdf: boedelverwerking_pres.md
	pandoc -t beamer "$<" -o "$@"

plantuml.jar:
	wget -O plantuml.jar http://sourceforge.net/projects/plantuml/files/plantuml.jar/download

%.png: %.uml plantuml.jar
	java -jar plantuml.jar "$<"
