'''
AGENT BROWSER
Easy way to browse through your characters folder and import them as
Agents for your Crowd simulation.

HOW IT WORKS:
This tool looks for .FBX files in your Agent Directory and lists them
in a UI.

You can then pick one or more characters from that list, and the following
nodes will be generated for each of them: Agent, Agent Clip, Agent Layer and Agent Prep.

Feel free to change the "agentDir" variable with your own Agent Directory.

IMPORTANT:
This code looks for subfolders too, so if you store your .FBX motion clips
in the same directory as your .FBX agents you may get some unexpected results.

In order to avoid that, make sure to have ONLY YOUR .FBX CHARACTERS in the
Agent Directory.
'''

import os
import sys
from collections import OrderedDict


############################
# SEARCHING FOR .FBX FILES #
############################


# Agent Directory: This is where your Agents are stored
agentDir = 'C:/Users/14385/3D Objects/characters'

# Initialize dictionary to store Agent names and file paths
dict = OrderedDict()

# Iterate through the Agent Directory and look at its path, subdirectories and files
for path,subdirs,files in os.walk(agentDir):
   
    # Iterate through the .FBX files and store their names and paths in the dictionary
    for file in files:
   
        if file.endswith('.fbx'):  
       
            agentName = file.split(".")
            agentName = agentName[0]                  
           
            filePath = os.path.join(path, file)
           
            dict[agentName] = filePath

# Open a "Select from list" window and ask the user to choose one or more agents
# NOTE: The output will be a tuple with index(es)
selectedAgents = hou.ui.selectFromList(dict.keys(),
                                title='Agent Browser',
                                message='Select the character(s) you want to import as agent(s):',
                                column_header='Agents',
                                width=300)

# If the user doesn't select any agent, stop the program                                
try:
    selectedAgents[0]
except IndexError:
    sys.exit()
   

#######################
# SET UP THE AGENT(S) #
#######################
   
   
# /obj/ context
obj = hou.node('/obj/')

# "agentSetup" node:
# This will help us determine if we should create the node
# or update the existing one
geoNodeName = 'agentSetup'
agentSetupNode = hou.node('{}/{}'.format(obj.path(), geoNodeName))

# If "agentSetup" doesn't exist, create it
if not agentSetupNode:
    agentSetupNode = obj.createNode('geo', geoNodeName)
   
# Iterate through every index in the "selectedAgents" tuple
for index in selectedAgents:

    # Agent node:
    # This will help us determine if we should create the node
    # or update the existing one
    agentNode = hou.node('{}/{}'.format(agentSetupNode.path(), dict.keys()[index]))
   
    # If the Agent node doesn't exist, create it
    if not agentNode:
        agentNode = agentSetupNode.createNode('agent', dict.keys()[index])
       
        # Set the Agent Name
        agentNode.parm('agentname').set('$OS')
       
        # Set Input as FBX and the file path
        agentNode.parm('input').set(2)
        agentNode.parm('fbxfile').set(dict.values()[index])
        agentNode.parm('fbxclipname').set('tpose')
   
        # Create an Agent Clip node and connect it to the Agent node
        agentClipNode = agentSetupNode.createNode('agentclip::2.0', '{}_clips'.format(dict.keys()[index]))
        agentClipNode.setInput(0, agentNode)

        # Create an Agent Layer node, connect it to the Agent Clip node
        # and activate the Source Layer checkbox so we can see the character
        agentLayerNode = agentSetupNode.createNode('agentlayer', '{}_layer'.format(dict.keys()[index]))
        agentLayerNode.setInput(0, agentClipNode)
        agentLayerNode.parm('sourcecopy').set(1)

        # Create an Agent Prep node and connect it to the Agent Layer node
        agentPrepNode = agentSetupNode.createNode('agentprep::3.0', '{}_prep'.format(dict.keys()[index]))
        agentPrepNode.setInput(0, agentLayerNode)

        # Create an OUT (Null) node and connect it to the Agent Prep node
        outNode = agentSetupNode.createNode('null', 'OUT_{}'.format(dict.keys()[index]))
        outNode.setInput(0, agentPrepNode)
        
        # Activate the Display/Render flags and set the color to black
        outNode.setDisplayFlag(True)
        outNode.setRenderFlag(True)
        outNode.setColor(hou.Color((0, 0, 0)))

        # Layout nodes inside "agentSetup"
        agentSetupNode.layoutChildren()

    # If the Agent node already exists in the scene, throw a message        
    else:
        hou.ui.displayMessage('The agent «{}» is already in your scene.'.format(dict.keys()[index]))