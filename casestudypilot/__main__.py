"""CLI entry point for casestudypilot."""

import json
import sys
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table

from casestudypilot.tools.youtube_client import fetch_video_data
from casestudypilot.tools.company_verifier import verify_company as verify_company_fn
from casestudypilot.tools.assembler import assemble_case_study
from casestudypilot.tools.validator import validate_case_study

app = typer.Typer(
    name="casestudypilot", help="CNCF Case Study Automation CLI", add_completion=False
)
console = Console()


@app.command()
def youtube_data(
    url: str = typer.Argument(..., help="YouTube video URL"),
    output: Path = typer.Option(
        Path("video_data.json"), "--output", "-o", help="Output JSON file path"
    ),
):
    """Fetch YouTube video data and transcript."""
    try:
        console.print(f"[cyan]Fetching video data from:[/cyan] {url}")
        data = fetch_video_data(url)

        # Write to file
        with open(output, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        console.print(f"[green]✓ Video data saved to:[/green] {output}")
        console.print(f"[dim]Video ID:[/dim] {data['video_id']}")
        console.print(f"[dim]Duration:[/dim] {data.get('duration_formatted', 'N/A')}")
        console.print(
            f"[dim]Transcript length:[/dim] {len(data.get('transcript', ''))} characters"
        )

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def verify_company(
    company_name: str = typer.Argument(..., help="Company name to verify"),
    output: Path = typer.Option(
        Path("company_verification.json"),
        "--output",
        "-o",
        help="Output JSON file path",
    ),
):
    """Verify if company is a CNCF end-user member."""
    try:
        console.print(f"[cyan]Verifying company:[/cyan] {company_name}")
        result = verify_company_fn(company_name)

        # Write to file
        with open(output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        console.print(f"[green]✓ Verification result saved to:[/green] {output}")

        # Display result
        if result["is_member"]:
            console.print(f"[green]✓ Company is a CNCF end-user member[/green]")
            console.print(f"[dim]Matched name:[/dim] {result['matched_name']}")
            console.print(f"[dim]Confidence:[/dim] {result['confidence']:.2f}")
        else:
            console.print(f"[red]✗ Company is NOT a CNCF end-user member[/red]")
            console.print(f"[dim]Best match:[/dim] {result['matched_name']}")
            console.print(f"[dim]Confidence:[/dim] {result['confidence']:.2f}")
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def assemble(
    video_data: Path = typer.Argument(..., help="Video data JSON file"),
    analysis: Path = typer.Argument(..., help="Analysis JSON file"),
    sections: Path = typer.Argument(..., help="Sections JSON file"),
    verification: Path = typer.Argument(..., help="Verification JSON file"),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output markdown file path (auto-generated if not specified)",
    ),
):
    """Assemble case study from component JSON files."""
    try:
        console.print("[cyan]Assembling case study...[/cyan]")
        result = assemble_case_study(
            video_data, analysis, sections, verification, output
        )

        console.print(f"[green]✓ Case study assembled:[/green] {result['output_path']}")
        console.print(f"[dim]Company:[/dim] {result['company_name']}")
        console.print(f"[dim]CNCF Projects:[/dim] {', '.join(result['cncf_projects'])}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def validate(
    case_study_path: Path = typer.Argument(..., help="Case study markdown file"),
    output: Path = typer.Option(
        Path("validation_results.json"), "--output", "-o", help="Output JSON file path"
    ),
    threshold: float = typer.Option(
        0.60, "--threshold", "-t", help="Minimum quality score threshold"
    ),
):
    """Validate case study quality."""
    try:
        console.print(f"[cyan]Validating case study:[/cyan] {case_study_path}")
        result = validate_case_study(case_study_path, threshold)

        # Write to file
        with open(output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        console.print(f"[green]✓ Validation results saved to:[/green] {output}")

        # Display result
        score = result["quality_score"]
        if result["passes"]:
            console.print(
                f"[green]✓ Quality score: {score:.2f}[/green] (threshold: {threshold:.2f})"
            )
        else:
            console.print(
                f"[red]✗ Quality score: {score:.2f}[/red] (threshold: {threshold:.2f})"
            )

        # Display warnings
        if result["warnings"]:
            console.print("\n[yellow]Warnings:[/yellow]")
            for warning in result["warnings"]:
                console.print(f"  • {warning}")

        # Display details table
        console.print("\n[cyan]Details:[/cyan]")
        table = Table()
        table.add_column("Category", style="cyan")
        table.add_column("Score", style="magenta")
        table.add_column("Status", style="green")

        for category, details in result["details"].items():
            status = "✓" if details["passed"] else "✗"
            table.add_row(
                category.replace("_", " ").title(), f"{details['score']:.2f}", status
            )

        console.print(table)

        if not result["passes"]:
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
