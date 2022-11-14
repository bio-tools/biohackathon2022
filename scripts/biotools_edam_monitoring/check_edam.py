from rdflib import ConjunctiveGraph
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import glob
import json
import argparse

VERBOSE=False

def remoteQuery(query, endpoint):
    endpoint.setQuery(query)
    try:
        result = endpoint.queryAndConvert()
        pd.set_option("display.max_rows",None,"display.max_colwidth",6000,"display.width",6000,)
        df = pd.DataFrame(result['results']['bindings'])
        df = df.applymap(lambda x: x['value'])
        return df
    except Exception as e:
        print(e)

def get_files(pattern):
    return glob.glob(pattern)

def pprint(message, **args):
    global VERBOSE
    if VERBOSE == True:
        print(message, **args)


def main():
    global VERBOSE

    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--endpoint', required=True, help="Define endpoint in format http(s)://endpoint:port/repositories/name")
    parser.add_argument('-f', '--file', help="File path to output data")
    parser.add_argument('-q', '--query', help="Path to files with queries in regex format, e.g. ./queries/*.query", default="./queries/*.query")
    parser.add_argument('-v', dest='verbose', action='store_true', default=False)
    args = parser.parse_args()

    VERBOSE = args.verbose

    ep_biotools = SPARQLWrapper(args.endpoint)
    ep_biotools.setReturnFormat(JSON)

    pprint("Running EDAM checks!")

    checks = get_files(args.query)
    pprint("Found query files: " + str(len(checks)))

    if len(checks) == 0:
        raise Exception("No queries were loaded.")

    results = {}

    for query_definition in checks:
        with open(query_definition, encoding = 'utf-8') as f:
            query = json.load(f)
            pprint("Running query: " + query["metadata"]["name"] + " " + "(id: "+query["metadata"]["id"]+").")
            q_results=remoteQuery(query=query["query"], endpoint=ep_biotools)
            output = ""
            if query["metadata"]["output_type"] == "listing":
                output = q_results.to_json(orient="records")
            elif query["metadata"]["output_type"] == "count":
                output = str(q_results["count"][0])
            results[query["metadata"]["id"]] = {"output_type": query["metadata"]["output_type"], "output": output}
            pprint("--> Results: " + output)
    
    if args.file:
        with open(args.file, mode="w", encoding = 'utf-8') as f:
            f.write(json.dumps(results))
    else:
        pprint("Final results:")
        print(json.dumps(results))

if __name__ == "__main__":
    main()
