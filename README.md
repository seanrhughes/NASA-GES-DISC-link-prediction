# NASA GES DISC Link Prediction

- This project was created over the course of my internship at NASA. I worked with the NASA Goddard Earth Sciences Data Information Center (GES DISC) to create 
a machine learning model that improves the archive's dataset navigation and discoverability. Over the next few months, my project
will be put into production by a full time engineer at NASA.<br><br>
- *Research for this project was presented at the 2024 American Meteorological Society (AMS) Conference*

## Background
The NASA Goddard Earth Sciences Data Information Center (GES DISC) archive is categorized via robust metadata. The most interesting of which is sets of 
science keywords given to a dataset, to characterize it's sphere of application. These science keywords are tags denoting what the dataset is about, 
examples include "humidity" "air pressure", "solar radiation", etc. There exists a possibility where these links may be missing where they otherwise should exist,
whether their absence was caused by incorrect input of data, the creation of new keywords, additions to the dataset, or anything else. A dataset that contains
missing science keywords is very bad for the archive, as it lowers the archive's ability to discover and recommend pertinent datasets to the user. This
project aims to solve this issue by creating a machine learning link prediction model, to predict missing dataset-science keyword linkages.

## Overview
This project was developed using `Python`, and `Neo4j`. We first produce a `Knowledge Graph` from the GES DISC archive, and use it in `Neo4j` to run various graph
algorithms and train the machine learning model.

## Knowledge Graph
<img src="https://github.com/seanrhughes/NASA-GES-DISC-link-prediction/assets/92600908/a0e314cd-b5b0-40a0-9159-9060628e89b1" width="400">

*Knowledge graph generated using GES DISC dataset metadata, with “Dataset” nodes in purple, 
“Keyword” nodes in blue, “Investigator” nodes in beige, “Platform” nodes in orange, and “Instrument” nodes in red.*
<br><br>
First, a knowledge graph is created from the GES DISC archive. Each "Dataset" node in purple, represents a dataset in the archive. These datasets most 
notably have a set of science keywords attached to it, but they also have other metadata such as the instrument the dataset used, the principal investigator
of the dataset, etc. This metadata is important information for the link prediction model to use when training, as the general assumption made is that
datasets that share similar investigators (or share similar instruments, etc) may be about similar topics.

## Link Prediction
The graph is first split into three subsets. First, a `feature-input set`, where node features are added to be trained and tested on by the model. These features 
consist of various graph algorithms, such as degree centrality, article rank, closeness centrality, etc. A `train set`, where the link prediction model 
trains via creating negative relationships in the graph, and a `test set` where the model tests itself. The winning model for this project 
used a `Random Forest` regression.

## Results
After training and testing, we see the link prediction model outputs:<br>

<img src="https://github.com/seanrhughes/NASA-GES-DISC-link-prediction/assets/92600908/d49f97e4-0e80-4566-870c-8287f6e92931">

<br>

We can see that the winning model has an average test score of `91 percent`.
<br><br>
This means on average the model is predicting each new dataset-science keyword link with 91 percent confidence. This score is much higher
than the random baseline score, which is considerably less than 50 percent. 
<br><br>
We can apply this winning model back to the graph to predict new dataset-science keyword linkages that were not present in the archive originally.<br>
We get hundreds of new linkages, each with their respective confidence score.<br><br>

<img src="https://github.com/seanrhughes/NASA-GES-DISC-link-prediction/assets/92600908/2f67b70b-9b2b-4d55-9c0c-279ae2e45b2c"> 
<br>

*Example predicted dataset-keyword linkage. The model predicts with 86 percent confidence that the 
AIRS/Aqua L2 Standard Physical Retrieval v006 (AIRH2RET) dataset should have the missing keyword “humidity”.*









