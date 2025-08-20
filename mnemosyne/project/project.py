from dataclasses import dataclass

from sqlalchemy import select, insert

from mnemosyne.knowledgebase.knowledgebase import KnowledgeBase
from mnemosyne.literature.literature import PaperInfo, Paper, LitSearch
from mnemosyne.researcher.researcher import Researcher, Manager

class ProjectNameError(Exception):
    pass


class Literature:
    """ same as apis just collecting all the methods in the literature module so that we can use them in the project class"""
    def __init__(self):
        self.litsearch=LitSearch()
        self.paper=Paper()


class Project:
    """
    this is the metaclass for the whole thing, it will collect all the modules and will be main point for interacting with the knowledgebase
    """
    def __init__(self, name, description, engine):
        """
        Main metaclass for consrcutor, if we are going to use any kind of agentic stuff the description is very important.
        The generated description of the project can be used to determine
        1. if a paper is relevant based on the abstract
        2. if a gene or a feature of a protein or a domain is relevant based on the description

        etc.

        This will be passed as part of the prompt for the project manger agent. The project description need to be set by a human,
        human can also provide an initial list of paper for the knowledgebase. All researchers will read all the abstracts and they
        will decide it is relevant or not. They will then look for full text papers to read among the relevant papers.

        :param description: A detailed desscription of the project, this will be used in all aspect of the agentic workflows
        it is not necessary to use agents but if you would like to automate a bunch of stuff than it might be helpful.
        """
        self.name = name
        self.project_id=None
        self.description = description
        self.kb = KnowledgeBase(engine=engine)
        self.literature = Literature()

    def _project_create(self):
        project_table = self.kb.db_tables["project"]
        query = select(project_table.c.project_id).filter(project_table.c.name == self.name)
        results = self.kb.session().execute(query).fetchall()

        if len(results) == 0:
            ins = insert(project_table).values(name=self.name, description=self.description).returning(
                project_table.c.project_id)
            self.project_id = self.kb.session().execute(ins).scalar()
        elif len(results) == 1:
            self.project_id = results[0][0]
        else:
            raise ProjectNameError("There are more than one projects with the same name")

    def _kb_create(self):
        self.kb._create_kb()



    #TODO
    def to_kb(self, data):
        if isinstance(data, PaperData):
            pass
        elif isinstance(data, Researcher) or isinstance(data, Manager):
            pass
        else:
            raise ValueError("Data type not supported")
