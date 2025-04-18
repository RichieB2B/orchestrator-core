from collections.abc import Generator
from typing import List, TypeAlias, cast

from orchestrator.domain.base import ProductBlockModel
from orchestrator.forms import FormPage
from orchestrator.forms.validators import MigrationSummary, migration_summary
from pydantic import ConfigDict


def summary_form(product_name: str, summary_data: dict) -> Generator:
    ProductSummary: TypeAlias = cast("type[MigrationSummary]", migration_summary(summary_data))

    class SummaryForm(FormPage):
        model_config = ConfigDict(title=f"{product_name} summary")

        product_summary: ProductSummary

    yield SummaryForm


def create_summary_form(user_input: dict, product_name: str, fields: List[str]) -> Generator:
    columns = [[str(user_input[nm]) for nm in fields]]
    yield from summary_form(product_name, {"labels": fields, "columns": columns})


def modify_summary_form(user_input: dict, block: ProductBlockModel, fields: List[str]) -> Generator:
    before = [str(getattr(block, nm)) for nm in fields]  # type: ignore[attr-defined]
    after = [str(user_input[nm]) for nm in fields]
    yield from summary_form(
        block.subscription.product.name,
        {
            "labels": fields,
            "headers": ["Before", "After"],
            "columns": [before, after],
        },
    )
