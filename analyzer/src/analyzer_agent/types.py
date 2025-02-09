from pydantic import BaseModel, Field


class Quote(BaseModel):
    text: str = Field(description="The text of the quote.")
    source: int = Field(
        description="The 1-based index of the source article in the sources list. For example, if the quote comes from the first article, this value would be 1."
    )
    relevance_justification: str = Field(
        description="Why this quote is relevant to the section and the report."
    )


class TopicBlueprint(BaseModel):
    title: str = Field(
        description="A concise title for this topic.",
    )
    description: str = Field(
        description="A detailed summary of the main points to be covered in this topic.",
    )
    supporting_articles_idxs: list[int] = Field(
        description="""Provide a list of **1-based indices** that point to the articles from the `<articles>` section that are most crucial for understanding and writing about this topic.  Think of this as creating a focused reading list for the writer agent: "To write about *this* topic effectively, the writer *must* consider *these* articles."  Be generous in your selection; it's better to include slightly more articles than to risk omitting key sources.  For example, if articles 1, 3, and 5 are essential, the list should be `[1, 3, 5]`."""
    )
    supporting_quotes: list[Quote] = Field(
        description="Between 2 and 10 quotes that exemplify key points to be used when writing this section."
    )


class TopicsBlueprints(BaseModel):
    topics: list[TopicBlueprint] = Field(
        description="A list of topics to be covered in the report."
    )
