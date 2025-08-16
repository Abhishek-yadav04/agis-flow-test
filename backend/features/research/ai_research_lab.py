class AIResearchLab:
    def __init__(self):
        self.experiments = 0
        self.papers_published = 0
    
    def get_research_stats(self):
        return {"experiments": self.experiments, "papers": self.papers_published}