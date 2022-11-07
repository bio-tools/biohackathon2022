INSTALLATION INSTRUCTIONS
=========================

These are the setup instructions that will allow you to run the notebooks available in this repository. Before starting to set this up, make sure you have **git** and **python** available on your machine.

Clone the repository
--------------------

From a shell, the command line should be:

`git clone git@github.com:bio-tools/biohackathon2022.git`

Set up Python dependencies and Jupyter
--------------------------------------

1. set up a virtual environment, and activate it!
This will prevent poluting your global python setup with libraries used only for this project

```
# navigate to the notebooks folder
cd biohackathon2022/notebooks
# set up virtualenv
python3 -m virtualenv .venv
# activate the virtualenv
. .venv/bin/activate
# (you can leave the virtualenv anytime if you type 'deactivate')
```

2. install python dependencies

we are going to use pip to install all python dependencies necessary to run jupyter and the notebooks

```
python -m pip install -r requirements.txt
```

3. run jupyter

just type the following in your shell:

```
jupyter-notebook
```

The jupyter server will launch, and the web interface will be available locally on http://localhost:8888/tree

You can also use VisualSudioCode to visualise and run the *.ipynb notebook files.

Congrats, you're done with jupyter!

Set up GraphDB
--------------

1. Go to the GraphDB website to download it

You should register with an online form at https://www.ontotext.com/products/graphdb/download/. You will then receive a download link by email, and choose the appropriate installer for your OS.

2. Run the GraphDB installer

3. Run GraphDB!

Set up a New GraphDB repository
---------------
On the left panel, go to "Setup" and "Repositories" to create a new repository.
Set up your graphDB repository name to "Project25" (so all partcipants have the same name, it avoid conflicts down the line)
Leave all default options for the GraphDB repository.

Import the Data
-----------------

Go to import on the left panel of graphDB, there you can upload bio.tools and EDAM from URL:

EDAM: https://raw.githubusercontent.com/edamontology/edamontology/main/EDAM_dev.owl

bio.tools: https://raw.githubusercontent.com/bio-tools/content/master/datasets/bioschemas-dump.ttl
