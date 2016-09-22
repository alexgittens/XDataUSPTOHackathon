#!/usr/bin/env python

"""
Functions for building and manipulating citation graphs.
"""

# Keith Levin
# September, 2016
# Johns Hopkins University
# klevin@jhu.edu

import pandas as pd
import pickle

class citation_graph(object):
    """
    Implements class of citation graphs.
    """

    def __init__(self, picklefile, use_applicant_cites ):
        """
        picklefile : pickle file containing the data frame to be read in.
            to row numbers (i.e., rows of the json dataframe).
        use_applicant_cites : boolean.
            If true, include the citations included by the applicant.
            If false, only use citations provided by the examiner.
        """

        # Read the data frame in.
        print 'Unpickling...',
        try:
            df = pd.read_pickle( picklefile )
        except TypeError:
            df = picklefile
        print 'done.'
        nrows = len(df)
        # Vertex and edge counters.
        self.vertex_count = 0
        self.edge_count = 0

        # Build the inverse lookup tables for row indices in the dataframe
        # based on patent and application document ids
        print 'Building lookup tables...',
        self.app2row = self.build_LUT( df, "patentApplicationDocNumber")
        self.grant2row = self.build_LUT( df, "publishedPatentDocNumber")
        # Maps a docnumber to a set of rows that cite that docnumber.
        self.citation_lookup = dict()
        print 'done.'
        
        # Go thru the rows of the data frame.
        self.neighbor_lookup = dict()
        self.ipcrtype = dict()
        self.app_numbers = dict()
        self.grant_numbers = dict()
        print 'Processing nodes',
        for rownum in range(nrows):
            if not self.is_vertex(rownum):
                self.add_vertex( rownum )
            thisrow = df.ix[rownum]
            # Process the examiner citations.
            exam_cites = thisrow['examinerCitations']
            self.process_citations( rownum, exam_cites )
            # Optionally process the applicant citations.
            if use_applicant_cites==True:
                app_cites = thisrow['applicantCitations']
                self.process_citations( rownum, app_cites )
            self.ipcrtype[rownum] = thisrow['ipcrType']
            self.app_numbers[rownum] = thisrow['patentApplicationDocNumber']
            self.grant_numbers[rownum] = thisrow['publishedPatentDocNumber']
            if rownum % 1000 == 0:
                print '.',
        print 'done.'

    def process_citations(self, rownum, citelist):
        """
        Try and add edges corresponding to all of the citations in the
        given list of citations.
        """
        for cite in citelist:
            if cite not in self.citation_lookup.keys():
                self.citation_lookup[cite] = set()
            # Create edges to any other docs that this cites.
            if cite in self.app2row:
                tgtid = self.app2row[cite]
                self.add_edge( rownum, tgtid )
            elif cite in self.grant2row:
                tgtid = self.grant2row[cite]
                self.add_edge( rownum, tgtid )
            # Form edges with any other nodes that cite the same citation.
            for v in self.citation_lookup[cite]:
                self.add_edge( rownum, v )
            # And want to map cite back to this row, since this row cites it. 
            self.citation_lookup[cite].add(rownum)

    def is_vertex( self, vx ):
        """
        Determine whether or not the given vertex is in the graph.
        """
        if vx in self.neighbor_lookup:
            return True
        else:
            return False

    def add_vertex( self, vx ):
        """
        Add this vertex to the graph.
        """
        self.neighbor_lookup[vx] = set()
        self.vertex_count = self.vertex_count + 1

    # Add an edge joining verteix vxaa and vxbb.
    # If either vertex doesn't exist, add it.
    def add_edge( self, vxaa, vxbb ):
        """
        Add an edge joining vertices vxaa and vxbb.
        """
        if not self.is_vertex(vxaa):
            self.add_vertex(vxaa)
        if not self.is_vertex(vxbb):
            self.add_vertex(vxbb)

        # Now actually add the edge.
        if vxbb not in self.get_neighbors(vxaa):
            self.neighbor_lookup[vxaa].add( vxbb )
            self.neighbor_lookup[vxbb].add( vxaa )
            self.edge_count = self.edge_count + 1

    def build_LUT( self, df, attr_name ):
        """
        Build a lookup table mapping the given attribute name attr_name
        back to rows numbers of the pandas data frame df.
        """
        LUT = {}
        elmts = df[attr_name].tolist()
        for (idx, docnum) in enumerate(elmts):
            LUT[docnum] = idx
        return LUT

    def get_neighbors( self, vx ):
        return self.neighbor_lookup[vx]
