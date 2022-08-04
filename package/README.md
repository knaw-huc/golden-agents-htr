# Named Entity Recognition Pipeline for the Golden Agents project

[![Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip)

This is a Named Entity Recognition tool for the Golden Agents project. It
ingests PageXML files (transcriptions of Handwritten Tech Recognition produced
by Transkribus) and subsequently extracts entities such as persons, objects,
materials, locations, etc.. from the data. The actual extraction is robust to spelling variation and
is conducted by [analiticcl](https://github.com/proycon/analiticcl).

The function of this NER pipeline is mainly to prepare the data to feed to
analiticcl, and to convert analiticcl's output to proper W3C Web Annotations.
