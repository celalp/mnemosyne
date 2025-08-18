---
layout: default
title: Roadmap
nav_order: 10
---

![Roadmap](assets/roadmap.png)

# Roadmap

This project is under heavy development. There are many features that are yet to be implemented. Apart from the literature
module none of the modules are yet functional.

Here is a "small" list of all the planned features:

- [ ] Storing the paper information in the database
- [ ] Spawning researchers
  - [ ] From huggingface
  - [x] From llamacpp and start/stop server
  - [ ] Connect to an existing model via requests (ollama or closed source models)
- [ ] Storing and re-creating reserachers
- [ ] Voting mechanisms, creating `smolagents` agents for voting
- [ ] Simple clustering methods of papers, themes and topics
- [ ] Extracting topics and themes with their respective rationale (structured llm output from researchers)
- [ ] unit tests and example dataset
- [ ] Documentation of all modules in detail and basic usage instructions


Here is a list of things that are **not** planned for the initial release:

- [ ] Using closed source models for embeddings (wast of tokens in my opinion)
- [ ] A nlp interface to talk to the researchers or the database (that's the job of the project class)
- [ ] A web interface
- [ ] An interface that supports multiple humans to interact with codebase, while any number of people 
in theory can connect to the database or share researchers, there is no tracking of who is connected to what. 


Please let me know if you have any suggestions or ideas.