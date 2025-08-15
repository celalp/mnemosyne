<div style="text-align: center;">
    <img src="assets/mnemosyne.png" width="900" alt="Mnemosyne talking to the 9 muses" class="center">
</div>

# Mnemosyne — An Integrated Assistant for Qualitative Research

Mnemosyne, the Titan goddess of memory, was the daughter of Uranus and Gaia and mother of the nine muses. Inspired by 
her role as the source of inspiration and knowledge, this project aims to bring together the different stages of qualitative 
research into one integrated system.

## Overview

Mnemosyne is an experimental framework designed to support the entire qualitative research process. By combining large 
language models (LLMs) with a modular architecture, it enables researchers to:

+ Search and process relevant literature.
+ Extract, organize, and analyze qualitative data.
+ Collaborate through multiple “researcher” agents with distinct strengths.
+ Reach consensus on topics and themes through a coordinated “manager” agent.

The goal is to replicate the strengths of human research teams while offloading the most tedious 
and repetitive tasks to AI, allowing researchers to focus on insight and interpretation.

## Motivation

Qualitative research is inherently collaborative and iterative. Mnemosyne seeks to capture that spirit by creating a 
cooperative AI environment where multiple specialized agents contribute to coding, synthesis, and interpretation.

By automating the labor-intensive steps — literature review, data extraction, initial coding — the system frees 
human researchers to focus on deeper insights.

## Core Modules

### 1. Project Meta Module

+ Stores project metadata in a database.
+ Initializes researcher agents and coordinates module workflows.
+ Acts as the interface between the user, database, and LLMs.

### 2. Literature Module

+ Searches scientific databases (currently PubMed and arXiv; more coming).
+ Filters papers by relevance, retrieves full texts when available, and extracts text, figures, and tables.
+ Stores structured outputs for later analysis.
+ Supports citation and reference graph expansion (note: grows exponentially).

### 3. Researcher Module

+ Each researcher is an LLM with slightly different goals, perspectives, or capabilities.
+ Researchers review abstracts, assess relevance, and extract key information.
+ Work in parallel to label sections of text with rationales.
+ A “manager” researcher consolidates and finalizes the coding results.
+ Produces two levels of analysis:
  + Topics — identified within individual documents.
  + Themes — groups of topics across the dataset.

## 4. Knowledge Base Module

+ Store all the data and literature related to a project. 
+ Stores all the metadata related to the researchers and how they are initiated.
+ Provides a centralized interface for all the data and metadata including embeddings for clustering data for 
visualizations. 
+ The knowledge base can be used for multiple projects and does not need to re-created every time. 



## Usage

For installation steps, please see the [installation guide](docs/installation.md).

Coming soon...