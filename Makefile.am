AM_CXXFLAGS = $(PICKY_CXXFLAGS)

common_source = graph.h

include_HEADERS = $(common_source)
bin_PROGRAMS = pifo_compiler

LDADD = $(libcgraph_LIBS)
pifo_compiler_SOURCES = $(common_source) pifo_compiler.cc
