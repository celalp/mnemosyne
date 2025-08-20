---
layout: default
title: Researcher
nav_order: 8
---

![Researcher Module](assets/researcher.png)

# Researcher Module

The researcher is an LLM with a very specific prompt that is in line with the overall objective of the project. The idea
is to generate `n` number of researchers with different skills and backgrounds that have come together to read all the relevant
documents and papers and code the results. 

This variability is generated in a number of ways. 

1. In the description of the [project](project.md) the user defined a set of goals in short sentences. Each researcher then
gets assigned a number of these goals in a way to make sure that there are overlapping goals between researchers and all of the 
goals are covered by at least one researcher. 
2. Each researcher is initialized using a unique prompt that is defined during the initialization of the researcher instance. 
This can be used to define the researchers' strengths and weaknesses to add additional variability. 
*Optional*
3. Based on these properties the researcher goes through all the abstracts that have been provided via the [litearture](literature.md)
module. The researcher then decided which papers are relevant to the project and their respective interests. Then again using the 
litarture module the researcher searches for full text papers and processes them in a ways that are described in the literture module. 

All this information constitutes the researcher's system prompt. Considering the extend and the diverstity that is represnted here
each researcher needs to have context window that is large enough to cover all the relevant information (which could be >100K tokens). 

Each researcher is responsible for 2 things:

1. Assigning a topic to each chunk of text that has been chunked for them by the "Manager" (see below). This assignment is 
more than just coming up with a word or a phrase. The researcher will return a dictionary in the following format

```python
chunk_topic={
    "topic": "<topic>", 
    "chunk": "<chunk text>",
    "explanation": "<explanation of the topic>"
}
```

2. 