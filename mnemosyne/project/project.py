from dataclasses import dataclass

from sqlalchemy import select, insert

from mnemosyne.knowledgebase.knowledgebase import KnowledgeBase
from mnemosyne.literature.literature import PaperInfo, Paper, LitSearch
from mnemosyne.researcher.researcher import Researcher, Manager

class ProjectNameError(Exception):
    pass

class Project:
    """
    this is the metaclass for the whole thing, it will collect all the modules and will be main point for interacting with the knowledgebase
    """
    def __init__(self, name, description, email, biogrid_api_key, engine):
        """
        Main metaclass for consrcutor, if we are going to use any kind of agentic stuff the description is very important.
        The generatl description of the project can be used to determine
        1. if a paper is relevant based on the abstract
        2. if a gene or a feature of a protein or a domain is relevant based on the description

        etc.

        This will be passed as part of the prompt for the project manger agent.

        :param description: A detailed desscription of the project, this will be used in all aspect of the agentic workflows
        it is not necessary to use agents but if you would like to automate a bunch of stuff than it might be helpful.
        """
        self.name = name
        self.project_id=None
        self.description = description
        self.kb = KnowledgeBase(engine=engine)
        self.papers=[]

    def _project_create(self):
        project_table=self.kb.db_tables["project"]
        query=select(project_table.c.project_id).filter(project_table.c.name==self.name)
        results=self.kb.session().execute(query).fetchall()

        if len(results)==0:
            ins=insert(project_table).values(name=self.name, description=self.description).returning(project_table.c.project_id)
            self.project_id=self.kb.session().execute(ins).scalar()
        elif len(results)==1:
            self.project_id=results[0][0]
        else:
            raise ProjectNameError("There are more than one projects with the same name")

        return self

    def _kb_create(self):
        self.kb._create_kb()

    def to_kb(self, items):
        """
        add things to the knowledgebase, these need to instances of some classes that are defined in the package, othewise
        you will get an error
        :param items:
        :return:
        """
        for item in items:
            if isinstance(item, Paper):
                add_papers(self, [item])
            elif isinstance(item, Researcher):
                add_researchers(self, [item])
            else:
                raise NotImplementedError("Items must be of type Paper, ApiCall, Molecule, Sequence, Structure, Variant or Genome")

    def from_kb(self, id, id_type):
        """
        generate an instance of something from the database, this assumes you know what you are looking for, as it will
        the autoincremented id of the thing. See the search method to get the ids you need.
        :param project_id:
        :param id:
        :param id_type:
        :return:
        """
        pass

    #def add_variants(self, variants):
    #    pass

    # for now we only can search papers and api calls because the import mechanism for sequence structures molecules
    # and variations is not yet implemented
    def search(self):
        pass

    def __str__(self):
        return f"Project(name:\n{self.name}\n\nproject_id:\n{self.project_id}\n\ndescription:\n{self.description})"

    def __repr__(self):
        return f"Project(name={self.name}, project_id={self.project_id}"
