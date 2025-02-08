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
    supporting_quotes: list[Quote] = Field(
        description="Between 2 and 10 quotes that exemplify key points to be used when writing this section."
    )


# class ReportOutline(BaseModel):
#     sections: list[TopicPlan] = Field(
#         description="An ordered list of sections that form the complete outline of the final report"
#     )
