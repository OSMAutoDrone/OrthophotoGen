# 1. verify docker installation
# 2. download odm image
# 3. create command
#      - ODM has lots of params
# 4. run command

import subprocess

# result = subprocess.run(
#     ["docker", "pull", "opendronemap/odm"],
#     capture_output=True,
#     text=True
# )
# print(result.stdout)

# command= [
#     "docker",
#     "run", 
#     "-ti", 
#     "--rm", 
#     "opendronemap/odm", 
#     "--help",
# ]

# NE PAS utiliser d'espace dans la commande, séparer en plusieurs string plutot
command= [  
    #docker params
    "docker",
    "run", 
    "-ti", 
    "--rm", 
    "-v", "C:/Users/simon/OneDrive/Uni/PMC/code/lvl1Correction/input:/datasets",
    "opendronemap/odm",
    #ODM params 
    "--project-path", "/datasets",
    "--orthophoto-compression", "NONE", 
    "--orthophoto-resolution", "0.01",
    "project"
]

result = subprocess.run(
    command,
    capture_output=True,
    text=True
)
print(result.stdout)
print(result.stderr)