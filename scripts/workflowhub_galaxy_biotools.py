import requests, json, re, itertools


###############
## Examples ###
###############

### workflow: https://workflowhub.eu/workflows/220.json
### galaxy API id: toolshed.g2.bx.psu.edu/repos/devteam/picard/picard_SamToFastq/2.18.2.2
### workflowhub step description: \n toolshed.g2.bx.psu.edu/repos/devteam/picard/picard_SamToFastq/2.18.2.2


#####################################
### Copied and modified code from ###
#####################################

### https://github.com/AustralianBioCommons/australianbiocommons.github.io/blob/master/finders/workflowfinder.py
### https://github.com/AustralianBioCommons/australianbiocommons.github.io/blob/master/finders/toolfinder.py


##############################################################
### Get WorkflowHub space workflows and extract Galaxy IDs ###
##############################################################

### Get BioCommons space workflows
available_data = {}
### https://stackoverflow.com/a/8685813
req = requests.get("https://workflowhub.eu/programmes/8/workflows.json")
if req.status_code != 200:
    raise FileNotFoundError(req.url)
### process request to get the workflow IDs
space_data = req.json()["data"]

### create an array with all the urls and request metadata
url_array = []
for workflow in space_data:
    id = workflow['id']
    link = workflow['links']['self']
    url = "https://workflowhub.eu%s.json" % link
    url_array.append((id, url))
for id, url in url_array:
    response = requests.get(url)
    if response.status_code != 200:
        raise FileNotFoundError(response.url)
    workflow_metadata = json.loads(response.text)
    available_data[id] = workflow_metadata

### filter for workflow_class Galaxy
galaxy_workflows = {}
for i in available_data:
    if available_data[i]['data']['attributes']['workflow_class']['key'] == "galaxy":
        galaxy_workflows[i] = available_data[i]

### extract unique workflow steps as Galaxy IDs
all_workflows_steps = {}
for i in galaxy_workflows:
    steps = available_data[i]['data']['attributes']['internals']['steps']
    workflow_steps = {}
    for j in range(0, len(steps)):
        description = steps[j]['description']
        ident = steps[j]['id']
        ### https://stackoverflow.com/a/12595082
        ### example toolshed ID toolshed.g2.bx.psu.edu/repos/iuc/minimap2/minimap2/2.20+galaxy2
        match_string = "toolshed.g2.bx.psu.edu/repos/.+/.+/.+/[0-9A-Za-z\\.\\+]{3,20}"
        if re.search(match_string, description):
            # https://stackoverflow.com/a/15340694
            pattern = re.compile(match_string)
            result = pattern.search(description)
            extracted_description = result.group(0)
            workflow_steps[ident] = extracted_description
        all_workflows_steps[i] = workflow_steps


#####################################################
### Access Galaxy API & extract ID + bio.tools ID ###
#####################################################

galaxy_api_req = requests.request("get", "https://usegalaxy.org.au/api/tools")
if galaxy_api_req.status_code != 200:
    raise FileNotFoundError(galaxy_api_req.url)
tool_sections = json.loads(galaxy_api_req.text)
### Herve Menager via Slack
tools_nested = [tool_section.get('elems') for tool_section in tool_sections if 'elems' in tool_section]
tools = list(itertools.chain.from_iterable(tools_nested))

tool_id_list = {}
for tool in tools:
    galaxy_id = tool["id"]
    biotools_id = None
    if "xrefs" in tool:
        for item in tool["xrefs"]:
            if item["reftype"] == "bio.tools":
                biotools_id = item["value"]
                break
    if biotools_id is not None:
        tool_id_list[galaxy_id] = biotools_id


###############################################
### from BH meeting discussion (2022-11-08) ###
###############################################

#### suggestion for queries (Herve) - output bioschemas compatible format - all in RDF
#### could put this in graphDB - and could generate queries

#### required metadata
##### workflow ID
##### do not remove duplicates
##### retain steps
##### step ID == galaxy ID
##### biotools ID

###############################################





