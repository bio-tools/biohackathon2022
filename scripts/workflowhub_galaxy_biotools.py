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

def galaxy_api_request(url):
    galaxy_api_req = requests.request("get", url)
    if galaxy_api_req.status_code != 200:
        raise FileNotFoundError(galaxy_api_req.url)
    tool_sections = json.loads(galaxy_api_req.text)
    ### Herve Menager via Slack
    tools_nested = [tool_section.get('elems') for tool_section in tool_sections if 'elems' in tool_section]
    tools = list(itertools.chain.from_iterable(tools_nested))
    return(tools)

def get_biotools_ID_from_galaxy_tools(galaxy_tools_list):
    galaxy_biotools_matches = {}
    for tool in galaxy_tools_list:
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
        else:
            galaxy_biotools_matches[galaxy_id_no_version] = None
    return(galaxy_biotools_matches)

########################
### GALAXY AUSTRALIA ###
########################
galaxy_AU_tools = galaxy_api_request(url = "https://usegalaxy.org.au/api/tools")
galaxy_AU_extracted_biotools_ids = get_biotools_ID_from_galaxy_tools(galaxy_tools_list = galaxy_AU_tools)


#####################
### GALAXY EUROPE ###
#####################
galaxy_Eu_tools = galaxy_api_request(url = "https://usegalaxy.eu/api/tools")
galaxy_Eu_extracted_biotools_ids = get_biotools_ID_from_galaxy_tools(galaxy_tools_list = galaxy_Eu_tools)


########################################
### Combined Galaxies bio.tools list ###
########################################

def combine_two_galaxy_tools_lists(extracted_biotools_list_1, extracted_biotools_list_2):

    combined_galaxy_biotools_matches = {}

    for galaxy_tool in extracted_biotools_list_1:
        biotools_id = extracted_biotools_list_1[galaxy_tool]
        combined_galaxy_biotools_matches[galaxy_tool] = biotools_id

    for galaxy_tool in extracted_biotools_list_2:
        if galaxy_tool not in combined_galaxy_biotools_matches:
            biotools_id = extracted_biotools_list_2[galaxy_tool]
            combined_galaxy_biotools_matches[galaxy_tool] = biotools_id

    return(combined_galaxy_biotools_matches)


eu_au_tools_list = combine_two_galaxy_tools_lists(galaxy_Eu_extracted_biotools_ids, galaxy_AU_extracted_biotools_ids)


##############################################################
### Get WorkflowHub space workflows and extract Galaxy IDs ###
##############################################################

def get_workflowhub_space_workflow_data(url):
    ### Get BioCommons space workflows
    ### https://stackoverflow.com/a/8685813
    req = requests.get(url)
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
        print(id)
        ### keep only Galaxy workflows!
        if workflow_metadata['data']['attributes']['workflow_class']['key'] == "galaxy":
            available_data[id] = workflow_metadata
            #print(id)

    return(available_data)


def extract_workflow_steps_as_galaxy_ids(workflowhub_data):
    ### extract unique workflow steps as Galaxy IDs
    all_workflows_steps = {}
    for i in workflowhub_data:
        steps = workflowhub_data[i]['data']['attributes']['internals']['steps']
        workflow_steps = {}
        for j in range(0, len(steps)):
            description = steps[j]['description']
            ident = steps[j]['id']
            #print(ident)
            #print(description)
            ### https://stackoverflow.com/a/12595082
            ### example toolshed ID toolshed.g2.bx.psu.edu/repos/iuc/minimap2/minimap2/2.20+galaxy2
            ### https://stackoverflow.com/a/4843178
            if isinstance(description, str):
                match_string = "toolshed.g2.bx.psu.edu/repos/.+/.+/.+/.+$"
                if re.search(match_string, description):
                    # https://stackoverflow.com/a/15340694
                    pattern = re.compile(match_string)
                    extracted_description = pattern.search(description)
                    extracted_galaxy_id = "/".join(extracted_description.group(0).split("/")[:-1])
                    workflow_steps[ident] = extracted_galaxy_id
                    all_workflows_steps[i] = workflow_steps
    return(all_workflows_steps)


biocommons_space_workflows = get_workflowhub_space_workflow_data(url = "https://workflowhub.eu/programmes/8/workflows.json")
biocommons_workflow_steps = extract_workflow_steps_as_galaxy_ids(workflowhub_data = biocommons_space_workflows)

all_workflows = get_workflowhub_space_workflow_data(url = "https://workflowhub.eu/workflows.json")
all_workflow_steps = extract_workflow_steps_as_galaxy_ids(workflowhub_data = all_workflows)


####################################################################################################################################
### final mapping for each Galaxy ID extracted from the workflows, what is the workflow ID, biotools ID and workflow step number ###
####################################################################################################################################

def map_workflow_steps_to_galaxy_biotools_ids(workflow_steps, biotools_IDs_from_galaxy):

    workflow_galaxy_biotools_map = {}
    COUNT_no_biotools_id_in_my_workflows = 0
    COUNT_biotools_id_in_my_workflows = 0
    COUNT_total_tools_in_my_workflows = 0
    COUNT_total_workflows = 0
    index = 0

    for workflow in workflow_steps:
        COUNT_total_workflows = COUNT_total_workflows + 1
        for step_number in workflow_steps[workflow]:
            workflow_galaxy_id = workflow_steps[workflow][step_number]
            if workflow_galaxy_id in biotools_IDs_from_galaxy and biotools_IDs_from_galaxy[workflow_galaxy_id] is not None:
                biotools_id = biotools_IDs_from_galaxy[workflow_galaxy_id]
                COUNT_biotools_id_in_my_workflows = COUNT_biotools_id_in_my_workflows + 1
                COUNT_total_tools_in_my_workflows = COUNT_total_tools_in_my_workflows + 1
            else:
                biotools_id = "no_biotools_id"
                COUNT_no_biotools_id_in_my_workflows = COUNT_no_biotools_id_in_my_workflows + 1
                COUNT_total_tools_in_my_workflows = COUNT_total_tools_in_my_workflows + 1
            workflow_data = {}
            workflow_data['workflow_galaxy_id'] = workflow_galaxy_id
            workflow_data['workflow_id'] = workflow
            workflow_data['biotools_id'] = biotools_id
            workflow_data['galaxy_workflow_step_number'] = step_number
            workflow_galaxy_biotools_map[index] = workflow_data
            index = index + 1

    print("##################################################")
    print("No. of workflow tools WITH a bio.tools ID = ", COUNT_biotools_id_in_my_workflows)
    print("No. of workflow tools without a bio.tools ID = ", COUNT_no_biotools_id_in_my_workflows)
    print("Total no. of workflow tools = ", COUNT_total_tools_in_my_workflows)
    print("Total no. of workflows = ", COUNT_total_workflows)
    print("##################################################")

    return(workflow_galaxy_biotools_map)


final_mapping_workflowhub_galaxy_biotools = map_workflow_steps_to_galaxy_biotools_ids(
    workflow_steps = all_workflow_steps,
    biotools_IDs_from_galaxy = eu_au_tools_list
)


def get_workflows_for_ttl_conversion(mapping_workflowhub_biotools):

    my_workflows = {}
    missing_biotools_IDs = []

    print("workflow ID / bio.tools ID :")

    for tool in mapping_workflowhub_biotools:
        data = mapping_workflowhub_biotools[tool]
        workflow = data['workflow_id']
        biotools_id = data['biotools_id']
        workflow_galaxy_id = data['workflow_galaxy_id']
        if biotools_id is not None and my_workflows.get(workflow, []) is not None:
            print(workflow, " / ", biotools_id)
            my_workflows[workflow] = my_workflows.get(workflow, []) + [biotools_id]
        else:
            missing_biotools_IDs.append(workflow_galaxy_id)

    print("##################################################")
    print("Galaxy tool IDs from workflows that are missing a bio.tools ID :")
    for id in missing_biotools_IDs:
        print(id)

    return(my_workflows)


all_workflows_for_ttl_conversion = get_workflows_for_ttl_conversion(
    mapping_workflowhub_biotools = final_mapping_workflowhub_galaxy_biotools
)


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


from rdflib import URIRef, BNode, Literal, Graph
from rdflib.namespace import SDO
g = Graph()
has_part = SDO.hasPart
for workflow_id, biotools_ids in all_workflows_for_ttl_conversion.items():
    for biotools_id in biotools_ids:
        workflow_ent = URIRef(f"https://workflowhub.eu/workflows/{workflow_id}?version=1")
        tool_ent = URIRef(f"https://bio.tools/{biotools_id}")
        g.add((workflow_ent, has_part, tool_ent))
g.serialize(destination="workflows_to_biotools.ttl")


###############################################





