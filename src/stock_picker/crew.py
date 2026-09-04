from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from pydantic import BaseModel, Field
from crewai_tools import SerperDevTool


def compact_search_tool() -> SerperDevTool:
    """Keep search context and free-tier usage bounded for each research agent."""
    return SerperDevTool(n_results=4, max_usage_count=4)


class TrendingCompany(BaseModel):
    """A company that is in the news and attracting attention."""
    name: str = Field(description="Company name")
    ticker: str = Field(description="Stock ticker symbol")
    reason: str = Field(description="Reason this company is trending in the news")


class TrendingCompanyList(BaseModel):
    """List of multiple trending companies that are in the news."""
    companies: list[TrendingCompany] = Field(description="List of companies trending in the news")


class TrendingCompanyResearch(BaseModel):
    """Detailed research on a company."""
    name: str = Field(description="Company name")
    market_position: str = Field(description="Current market position and competitive analysis")
    future_outlook: str = Field(description="Future outlook and growth prospects")
    investment_potential: str = Field(description="Investment potential and suitability for investment")


class TrendingCompanyResearchList(BaseModel):
    """A list of detailed research on all the companies."""
    research_list: list[TrendingCompanyResearch] = Field(description="Comprehensive research on all trending companies")


@CrewBase
class StockPicker():
    """StockPicker crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    def __init__(self, llm):
        self.llm = llm

    @agent
    def trending_company_finder(self) -> Agent:
        return Agent(config=self.agents_config['trending_company_finder'],
                     llm=self.llm, tools=[compact_search_tool()], verbose=True,
                     max_iter=5, max_retry_limit=1)

    @agent
    def financial_researcher(self) -> Agent:
        return Agent(config=self.agents_config['financial_researcher'],
                     llm=self.llm, tools=[compact_search_tool()], verbose=True,
                     max_iter=6, max_retry_limit=1)

    @agent
    def stock_picker(self) -> Agent:
        return Agent(config=self.agents_config['stock_picker'],
                     llm=self.llm, verbose=True,
                     max_iter=4, max_retry_limit=1)

    @task
    def find_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['find_trending_companies'],
            output_pydantic=TrendingCompanyList,
        )

    @task
    def research_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['research_trending_companies'],
            output_pydantic=TrendingCompanyResearchList,
        )

    @task
    def pick_best_company(self) -> Task:
        return Task(
            config=self.tasks_config['pick_best_company'],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the StockPicker crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            tracing=False,
        )
