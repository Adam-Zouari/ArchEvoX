"""Jinja2 template rendering for the markdown portfolio report."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from models.schemas import Portfolio

_templates_dir = Path(__file__).resolve().parent.parent / "templates"


def render_portfolio_report(portfolio: Portfolio) -> str:
    """Render the portfolio into a markdown report using the Jinja2 template."""
    env = Environment(
        loader=FileSystemLoader(str(_templates_dir)),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("portfolio_report.md.j2")
    return template.render(portfolio=portfolio)
