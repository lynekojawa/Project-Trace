# Project-Trace
(7/1)<br>
Initialized the plan and will start working on it from tomorrow<br>
(7/2)<br>
Initialized the project, and move Orion to flash-extended, and I thought this applies for all <br>
apparently is not, you need to check every time, <br>
Creating a directories: Engine, parsar and ui <br>
There was miscommunication somewhere so Orion(planner) provide me the code for scanning file, while my first output I want this to be analogic.<br>
made PODO to write memorandum to Orion to fix. I have noticed about this miscommunicating alot more from last project. which tells me human role <br>
is very crucial where to stop and where to continue. <br> 
Why is AI have hard time to use two languages in once? <br>
(7/7)<br>
Continuing on project. <br>
Resized the canvas space, currently drawing FILE, FUNC. Phase 1: completed-except Dante Review. <br>
Opened GPT PODO so that I can get another critical reviewer and strategic partner. <br> 
add __init__.py for all folders ui, components, engine<br> 
fixed 1 of 2 issues from GPT PODO's comment, there were minor indentation issue at canvas py. so potential_parent was not active<br> 
memorendum from podo to Orion, Phase 2.5 initiated to enhance and adding 1. save, load and 2. edge arrow<br>
(7/8) <br>
Starting with continuing the phase 2.5 ui connection. <br>
New class BluepringEdgeItem to separate node and edge. <br>
Around 260K token Podo started drift, e.g deleting canvas, or functions, I feel like he was working very well btw 150K-230K with all context and logics and codes<br>
Currently, I can save and load, with different file name. Drawing folder/ node/ edges are looking good. however, when I load it only loads the nodes no edges. <br>
(7/9)<br>
yesterday I left it from it creates the edges and vertices and it is very flexible. and currently when I load the json it loads all nodes but not edges, that's where to start<br>
Fixed, edge is now up whenever I reload the savedfile. Surprisingly I like my agent more even if he had 319K tokens <br> 
I feel like the relationship and some features are not enough before I am move to phase 4,5 with orion I am planning to implement the following features<br>
1. Delete node and edge 2. Edge color by relationship Call(Green), Import(Blue), External(Purple), Read/Write(Yellow)<br>
3. Edge Label(CAll/Import/Read/Write)<br> 
started on implementing deleting node add remove_node into repository_graph.py<br>
Currently it removes nodes is possible, edge is not. Updated both remove node and edge is possible<br>
ISSUE: when load the file, it loads the deleted node, no issues with deleted_edge<br>
(7/13)<br>
Continue from last issue here are today's todo list.<br>
1. debug with Dante (x)
2. fix the file load (x) it was self.graph.remove_node(node.node_id) line creating a problem. <br>
3. coloring edge and label edge. (x) add the colors in canvas.py and updated ui <br>
Heavist room I ever reached with podo 360K<br>
After playing with this changes here are the things I am going to work on next few day. <br>
1. add class node, and folder node, and external node
2. Size up function, variable box
3. arrow <-, <->
4. safeguard add feature when there are same name, can't add
5. zoom in, zoom out canvas
6. node filtering(layer)
Current status: satisfied with progress, but found uncomfortable part from tomorrow
Tomorrow todo: 1,2,4 -> 3-> 5,6<br>
(7/14)<br> 
Todo List
1. Debug with Dante(x)
2. Add class, folder, external node(x)
3. Size up function, variable box (x)
4. safe guard add feature when there are same name, can't add(x)
(7/15)<br>
FIXED CLASS NODE OFF positioning when load the file: child_item.setPos(parent_item.mapFromScene(node.x, node.y))<br>
Changed above code into child_item.setPos(node.x, node.y), somehow this converts and reconverts and this masses the position up, <br> 
Todo List
1. Zoom in, Zoom out(x)
2. arrow( Progress, updated engine, canvas, workbench -/ is the how arrow looks like <-> doesn't appear, debug needed)<br> 
3. node filtering
(7/20)<<br>
Continuing on project todo list:
1. Arrow: triangle issue resolved it is now looking like ->, the problem wasfrom polygone it is now changed <br>
Working on bidirectional <-> it is lost from somewhere but not sure. a minor tracks n all the edge_item<br>
updated workbench to delete <-> edge. <br>
2. Node filtering