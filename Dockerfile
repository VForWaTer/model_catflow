# ============================================================================
# CATFLOW model container -  Python tool template + gfortran build
# ============================================================================

# ---- Stage 1: build gotap ---------------------------------------------------
FROM golang:1.25-alpine AS gotap-builder
RUN apk add --no-cache git
ARG GOTAP_VERSION=main
RUN git clone --depth 1 --branch ${GOTAP_VERSION} https://github.com/tool-spec/gotap.git /gotap && \
    cd /gotap && go build -o gotap .

# ---- Stage 2: BUILD CATFLOW with gfortran (compiler NOT shipped) ------------
FROM gcc:14 AS catflow-build
COPY ./src/catflow_gnu/ /src/catflow/
WORKDIR /src/catflow
RUN gfortran -mcmodel=medium -ffixed-form -ffixed-line-length-132 \
    -std=legacy -O2 *.FOR *.for -o /catflow.exe

# ---- Stage 3: RUNTIME - python:3.12 (includes python3 + apt) ---------------
FROM python:3.12
COPY --from=gotap-builder /gotap/gotap /usr/local/bin/gotap
RUN chmod +x /usr/local/bin/gotap

# gfortran runtime libs CATFLOW needs (free/redistributable)
RUN apt-get update && apt-get install -y --no-install-recommends \
      libgfortran5 libgomp1 libgcc-s1 libc6 \
    && rm -rf /var/lib/apt/lists/*

# python deps for generated bindings
RUN python3 -m pip install --no-cache-dir numpy pandas click

# compiled CATFLOW binary
COPY --from=catflow-build /catflow.exe /usr/local/bin/catflow.exe
RUN chmod +x /usr/local/bin/catflow.exe

# create the tool input structure
RUN mkdir /in
COPY ./in /in
RUN mkdir /out
RUN mkdir /src
COPY ./src /src

# Generate parameter bindings from tool.yml at build time (replaces json2args)
WORKDIR /src
RUN gotap generate --spec-file=tool.yml --target=python --output=parameters.py

# copy the citation file - looks funny to make COPY not fail if the file is not there
COPY ./CITATION.cf[f] /src/CITATION.cff

WORKDIR /src
CMD ["gotap", "run", "catflow", "--input-file", "/in/input.json"]
