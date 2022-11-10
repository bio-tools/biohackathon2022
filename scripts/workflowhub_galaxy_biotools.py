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

galaxy_biotools_matches = {}
for tool in tools:
    galaxy_id = tool["id"]
    galaxy_id_no_version = "/".join(galaxy_id.split("/")[:-1])
    biotools_id = None
    if "xrefs" in tool:
        for item in tool["xrefs"]:
            if item["reftype"] == "bio.tools":
                biotools_id = item["value"]
                break
    if biotools_id is not None:
        galaxy_biotools_matches[galaxy_id_no_version] = biotools_id


##############################################################
### Get WorkflowHub space workflows and extract Galaxy IDs ###
##############################################################

### Get BioCommons space workflows
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

available_data = {}

for id, url in url_array:
    response = requests.get(url)
    if response.status_code != 200:
        raise FileNotFoundError(response.url)
    workflow_metadata = json.loads(response.text)
    ### keep only Galaxy workflows!
    if workflow_metadata['data']['attributes']['workflow_class']['key'] == "galaxy":
        available_data[id] = workflow_metadata

### extract unique workflow steps as Galaxy IDs
all_workflows_steps = {}
for i in available_data:
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
            extracted_description = pattern.search(description)
            extracted_galaxy_id = "/".join(extracted_description.group(0).split("/")[:-1])
            workflow_steps[extracted_galaxy_id] = ident
        all_workflows_steps[i] = workflow_steps

####################################################################################################################################
### final mapping for each Galaxy ID extracted from the workflows, what is the workflow ID, biotools ID and workflow step number ###
####################################################################################################################################

workflow_galaxy_biotools_map = {}

for workflow in all_workflows_steps:
    #print("workflow:", workflow)
    for wfh_galaxy_id in all_workflows_steps[workflow]:
        #print("wfh_galaxy_id:", wfh_galaxy_id)
        step_number = all_workflows_steps[workflow][wfh_galaxy_id]
        if wfh_galaxy_id in galaxy_biotools_matches:
            biotools_id = galaxy_biotools_matches[wfh_galaxy_id]
        else:
            biotools_id = None
        print(biotools_id)
        workflow_data = {}
        workflow_data['workflow_id'] = workflow
        workflow_data['biotools_id'] = biotools_id
        workflow_data['galaxy_workflow_step_number'] = step_number
        workflow_galaxy_biotools_map[wfh_galaxy_id] = workflow_data

###################
### some counts ###
###################

### number of workflows
len(all_workflows_steps)

### number of workflow tools (i.e. Galaxy IDs)
len(workflow_galaxy_biotools_map)

### number of workflow tools with biotools IDs
biotools_count = 0
for i in workflow_galaxy_biotools_map:
    if workflow_galaxy_biotools_map[i]['biotools_id'] is not None:
        biotools_count = biotools_count + 1
print(biotools_count)

### % of workflow tools with biotools IDs
print(round((biotools_count/len(workflow_galaxy_biotools_map))*100))


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





