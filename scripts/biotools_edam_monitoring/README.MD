# Demo of framework for continuos integration
This is demo of a script, that could be run periodicaly and monitor important metrics about EDAM and it's usage in bio.tools.

## How to run
```
pip3 install -r requirements.txt
```
To run checks
```
cd ./scripts/biotools_edam_monitoring
python3 check_edam.py -e http://localhost:7200/repositories/Project25
```
## Available arguments
| Argument | Description |
| -------- | ----------- |
  -h, --help |           show this help message and exit
| -e, --endpoint | GraphDB endpoint with repository name, e.g. __http://localhost:7200/repositories/Project25__ |
| -f, --file | Path to file, where JSON output is stored |
| -q, --query | Pattern where query files are stored e.g. __./queries/*.query__ |
| -v | shows debug information while running script |

## Sample of query definition file
```json
{
    "metadata": {
        "id": "ID OF THE METRIC",
        "description": "METRIC DESCRIPTION",
        "name": "NAME OF THE METRIC",
        "output_type": "listing/count"
    },
    "query": "SPARQL QUERY - WITHOUT LINE-BREAKS"
}
```

## Contact
Contact me at adrian(at)ics.muni.cz