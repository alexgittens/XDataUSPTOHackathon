# XDataUSPTOHackathon
USPTO-centric XData Hackathon from September 2016

Use createGrantInfoDataFrame.py to extract the relevant data from the xml source files and convert to a Pandas DataFrame
Use generate_one_hop_adjacency_matrix.ipynb to generate a one-hop adjacency matrix based on patents citing each other or citing the same patent; it exports this adjacency matrix and a subset to be used for training the classifier (this also cluster using stochastic block modeling)
