# CATFLOW Hydrological Model

This repository packages the CATFLOW hydrological model as a Docker container. CATFLOW simulates water flow and transport in hillslopes and catchments, including subsurface flow and overland flow.

The Fortran model is compiled with `gfortran` when the image is built. The resulting container includes the compiled model and a [`gotap`](https://github.com/tool-spec/gotap)-based interface that follows the [Tool Specification](https://vforwater.github.io/tool-specs/).

## What the container does

The container runs the CATFLOW model with the input files mounted at `/in` and writes model results and run metadata to `/out`.
The tool reads `/in/input.json`, which identifies the input directory and simulation ID:

```json
{
  "catflow": {
    "parameters": {
      "simulation_id": "initial_simulation"
    },
    "data": {
      "inp_dir": "/in"
    }
  }
}
```

CATFLOW also requires the control files `catflow.in` and `run_cat.in` in `/in`, along with the data files and subdirectories referenced by those control files. Keep the model's expected directory and file names when preparing a different input set.

## Build and run

You need Docker installed and running.

Build the image from the repository root:

```sh
docker build -t catflow-model .
```

Run it with the repository's input and output directories mounted into the container.

**PowerShell:**

```powershell
docker run --rm -it `
  -v "${PWD}/in:/in" `
  -v "${PWD}/out:/out" `
  -e TOOL_RUN=catflow `
  catflow-model
```

**Linux/macOS shell:**

```sh
docker run --rm -it \
  -v "$PWD/in:/in" \
  -v "$PWD/out:/out" \
  -e TOOL_RUN=catflow \
  catflow-model
```

Replace files in the local `in/` directory with your own input data before running. CATFLOW writes its model log to `out/log.out`; the tool also writes run metadata and structured logs in `out/`.


## Input and output directories

| Path | Purpose |
| --- | --- |
| `in/input.json` | Tool parameters and path to the model input directory |
| `in/catflow.in` | CATFLOW control file |
| `in/run_cat.in` | CATFLOW run configuration |
| `in/` subdirectories and data files | Model inputs referenced by the CATFLOW control files |
| `out/` | CATFLOW results, including `log.out`, plus `gotap` metadata and structured logs |

The host `in/` and `out/` directories are mounted into the container. Generated files therefore remain available on the host after the container exits.

## Development

- `Dockerfile` compiles the Fortran sources in `src/catflow_gnu/` and builds the runtime image.
- `src/tool.yml` defines the tool interface.
- `src/run.py` launches the compiled CATFLOW executable.

After changing the model or container configuration, rebuild the image with `docker build -t catflow-model .`.

## References

- [CATFLOW project](https://github.com/CATFLOW)
- [CATFLOW preprocessing and postprocessing tools](https://github.com/VForWaTer/tool_catflow)
- [VForWaTer Tool Specification](https://vforwater.github.io/tool-specs/)

## License

See [LICENSE](LICENSE) for this repository's license. The CATFLOW model sources are included in `src/catflow_gnu/`; consult the upstream project for applicable model licensing and attribution.
