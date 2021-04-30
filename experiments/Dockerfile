FROM proycon/lamachine:core
MAINTAINER Maarten van Gompel <proycon@anaproy.nl>
LABEL description="Development environment for Golden Agents experiments"
#RUN lamachine-config lm_base_url https://your.domain.here
#RUN lamachine-config force_https yes
#RUN lamachine-config private true
#RUN lamachine-config maintainer_name "Your name here"
#RUN lamachine-config maintainer_mail "your@mail.here"
RUN lamachine-add languagemachines-basic
RUN lamachine-add languagemachines-rust
RUN lamachine-add python-core
RUN lamachine-update
RUN pip install SPARQLWrapper
CMD /bin/bash -l
