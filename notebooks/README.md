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

Import the data
---------------

leave all default options for the GraphDB repository.
