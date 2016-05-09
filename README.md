pifo-compiler:
	-run as : python pifo_compiler.py example.dot
	- output: 
		-examplecompilation.cc <- pifo-machine compatible
		-exampleEnqueues.gv.pdf
		-printout of mesh configuration
	-input reqs:
		-nodes as PIFOs
		-directed edges from parent to child in tree structure
		-each node has unique name
		- names are valid variable names in C++
		- each node has attributes shaping, schedule, and predicate
		- predicate either of form "True" or "p.class==match"
		- schedule is valid c++ function acting on field container x
		- shaping "NULL" or valid c++ function action on field container x

mahi-compiler:
	-run as : python mahi_compiler.py example.dot
	- output: 
		-exampleMahicompilation.cc <- pifo-machine compatible
		-exampleEnqueues.gv.pdf
		-printout of mesh configuration
	-input reqs:
		-nodes as PIFOs
		-directed edges from parent to child in tree structure
		-each node has unique name
		- names are valid variable names in C++
		- each node has attributes shaping, schedule, and predicate
		- predicate either of form "True" or "p.class==match"
		- schedule is valid c++ function acting on QueuedPacket x
		- shaping "NULL" or valid c++ function action on QueuedPacket x

