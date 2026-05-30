# Ababeel Electronic Support, Electronic Warfare (ES/EW)

daffodil unparse -s ../faketdl/src/fakeTDL.dfdl.xsd -o j32_payload.bin es-log.xml

## Running the Project Locally

We use Poetry to manage dependencies. Follow these concise steps to use it:

### 1. Activating the Environment
Since Poetry 2.0.0, `poetry shell` is deprecated. Use this to activate your environment in your shell:
```bash
source $(poetry env info --path)/bin/activate
```
Or, simply prefix your commands with `poetry run`:
```bash
poetry run python mother/main.py --simulate
```
