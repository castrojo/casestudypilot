"""CLI entry point for casestudypilot."""

import json
import sys
from pathlib import Path
from typing import Optional, List
import typer
from rich.console import Console
from rich.table import Table

from casestudypilot.tools.youtube_client import fetch_video_data
from casestudypilot.tools.company_verifier import verify_company as verify_company_fn
from casestudypilot.tools.assembler import assemble_case_study
from casestudypilot.tools.validator import validate_case_study
from casestudypilot.tools.screenshot_extractor import (
    extract_screenshots as extract_screenshots_fn,
)
from casestudypilot.tools.frame_extractor import extract_frame_at_timestamp
from casestudypilot.validation import (
    validate_transcript as validate_transcript_fn,
    validate_company_name as validate_company_name_fn,
    validate_analysis as validate_analysis_fn,
    validate_metrics as validate_metrics_fn,
    validate_company_consistency as validate_company_consistency_fn,
    Severity,
)
from casestudypilot.tools.validate_deep_analysis import main as validate_deep_analysis_main
from casestudypilot.tools.validate_reference_architecture import main as validate_reference_architecture_main
from casestudypilot.tools.assemble_reference_architecture import main as assemble_reference_architecture_main
from casestudypilot.tools.github_client import fetch_github_profile, get_profile_completeness
from casestudypilot.tools.multi_video_processor import fetch_multi_video_data
from casestudypilot.tools.profile_assembler import assemble_presenter_profile
from casestudypilot.tools.issue_parser import parse_issue
# TODO: Implement these validation modules (future tasks)
# from casestudypilot.validation.presenter import validate_presenter
# from casestudypilot.validation.biography import validate_biography
# from casestudypilot.validation.profile_update import validate_profile_update
# from casestudypilot.validation.presenter_profile import validate_presenter_profile

app = typer.Typer(name="casestudypilot", help="CNCF Case Study Automation CLI", add_completion=False)
console = Console()


@app.command()
def youtube_data(
    url: str = typer.Argument(..., help="YouTube video URL"),
    output: Path = typer.Option(Path("video_data.json"), "--output", "-o", help="Output JSON file path"),
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
        console.print(f"[dim]Transcript length:[/dim] {len(data.get('transcript', ''))} characters")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command(name="parse-issue")
def parse_issue_cmd(
    issue_number: int = typer.Argument(..., help="GitHub issue number"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output JSON file path"),
):
    """Parse GitHub issue and extract content generation metadata.

    Extracts YouTube URL, content type, company name, and other metadata
    from GitHub issues created via content generation templates.

    Example:
        python -m casestudypilot parse-issue 42
        python -m casestudypilot parse-issue 42 --output issue_data.json
    """
    try:
        console.print(f"[cyan]Parsing issue:[/cyan] #{issue_number}")
        result = parse_issue(issue_number)

        # Write to file if specified
        if output:
            with open(output, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
            console.print(f"[green]✓ Issue data saved to:[/green] {output}")

        # Display result
        console.print(f"\n[bold]Issue #{result['issue_number']}[/bold]")
        console.print(f"[dim]Title:[/dim] {result['title']}")
        console.print(f"[dim]Content Type:[/dim] {result['content_type']}")
        console.print(f"[dim]Video URL:[/dim] {result['video_url']}")

        if result.get("company_name"):
            console.print(f"[dim]Company:[/dim] {result['company_name']}")
        else:
            console.print(f"[dim]Company:[/dim] [yellow]Not specified (will extract from video)[/yellow]")

        # Output JSON to stdout if no file specified
        if not output:
            console.print(f"\n[dim]JSON output:[/dim]")
            console.print(json.dumps(result, indent=2))

    except ValueError as e:
        console.print(f"[red]Validation Error:[/red] {e}")
        sys.exit(2)
    except RuntimeError as e:
        console.print(f"[red]Runtime Error:[/red] {e}")
        sys.exit(2)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(2)


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
    screenshots: Optional[Path] = typer.Option(
        None,
        "--screenshots",
        "-s",
        help="Screenshots JSON file (optional)",
    ),
):
    """Assemble case study from component JSON files."""
    try:
        console.print("[cyan]Assembling case study...[/cyan]")
        result = assemble_case_study(video_data, analysis, sections, verification, output, screenshots)

        console.print(f"[green]✓ Case study assembled:[/green] {result['output_path']}")
        console.print(f"[dim]Company:[/dim] {result['company_name']}")
        console.print(f"[dim]CNCF Projects:[/dim] {', '.join(result['cncf_projects'])}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command(name="extract-screenshots")
def extract_screenshots_cmd(
    video_data: Path = typer.Argument(..., help="Video data JSON file"),
    analysis: Path = typer.Argument(..., help="Analysis JSON file"),
    sections: Path = typer.Argument(..., help="Sections JSON file"),
    download_dir: str = typer.Option(..., "--download-dir", "-d", help="Directory to download screenshots to"),
    output: Path = typer.Option(Path("screenshots.json"), "--output", "-o", help="Output JSON file path"),
):
    """Extract and download screenshots from video."""
    try:
        console.print("[cyan]Extracting screenshots...[/cyan]")
        result = extract_screenshots_fn(video_data, analysis, sections, output, Path(download_dir))

        console.print(f"[green]✓ Screenshots extracted:[/green] {output}")
        console.print(f"[dim]Company:[/dim] {result['company_slug']}")
        console.print(f"[dim]Screenshots:[/dim] {len(result['screenshots'])}")

        # Display screenshot details
        for screenshot in result["screenshots"]:
            section = screenshot["section"]
            success = screenshot["download_success"]
            status = "[green]✓[/green]" if success else "[red]✗[/red]"
            console.print(f"  {status} {section.title()}: {screenshot['local_path']}")
            if not success:
                console.print(f"    [red]Error:[/red] {screenshot.get('download_error')}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command(name="extract-screenshot")
def extract_screenshot_cmd(
    video_url: str = typer.Argument(..., help="YouTube video URL"),
    timestamp: int = typer.Argument(..., help="Timestamp in seconds"),
    output: Path = typer.Argument(..., help="Output file path (e.g., screenshots/screenshot-1.jpg)"),
):
    """Extract single screenshot from video at specific timestamp.
    
    This command is designed for agent workflows that need to extract
    individual frames. For batch extraction, use extract-screenshots instead.
    
    Example:
        python -m casestudypilot extract-screenshot \\
            'https://youtube.com/watch?v=VIDEO_ID' \\
            450 \\
            'screenshots/screenshot-1.jpg'
    """
    try:
        console.print(f"[cyan]Extracting screenshot at {timestamp}s...[/cyan]")

        # Create output directory
        output.parent.mkdir(parents=True, exist_ok=True)

        # Extract frame
        result = extract_frame_at_timestamp(video_url=video_url, timestamp_seconds=timestamp, output_path=output)

        if result["success"]:
            file_size_kb = result.get("file_size", 0) / 1024
            console.print(f"[green]✓ Screenshot saved to:[/green] {output}")
            console.print(f"[dim]File size:[/dim] {file_size_kb:.1f} KB")
            console.print(f"[dim]Method:[/dim] {result.get('method', 'frame_extraction')}")
        else:
            console.print(f"[red]✗ Screenshot extraction failed[/red]")
            console.print(f"[red]Error:[/red] {result.get('error', 'Unknown error')}")
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def validate(
    case_study_path: Path = typer.Argument(..., help="Case study markdown file"),
    output: Path = typer.Option(Path("validation_results.json"), "--output", "-o", help="Output JSON file path"),
    threshold: float = typer.Option(0.60, "--threshold", "-t", help="Minimum quality score threshold"),
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
            console.print(f"[green]✓ Quality score: {score:.2f}[/green] (threshold: {threshold:.2f})")
        else:
            console.print(f"[red]✗ Quality score: {score:.2f}[/red] (threshold: {threshold:.2f})")

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
            table.add_row(category.replace("_", " ").title(), f"{details['score']:.2f}", status)

        console.print(table)

        if not result["passes"]:
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command(name="validate-transcript")
def validate_transcript_cmd(
    video_data: Path = typer.Argument(..., help="Video data JSON file"),
):
    """Validate transcript quality from video data file."""
    try:
        console.print(f"[cyan]Validating transcript from:[/cyan] {video_data}")

        # Load video data
        with open(video_data, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Validate transcript
        result = validate_transcript_fn(data.get("transcript", ""), data.get("transcript_segments", []))

        # Display result
        console.print(f"\n[bold]Validation Status:[/bold] {result.status.value}")

        if result.is_critical():
            console.print("\n[red bold]CRITICAL ERRORS:[/red bold]")
        elif result.has_warnings():
            console.print("\n[yellow bold]WARNINGS:[/yellow bold]")
        else:
            console.print("\n[green bold]ALL CHECKS PASSED[/green bold]")

        # Display checks
        for check in result.checks:
            if not check.passed:
                icon = "✗" if check.severity == Severity.CRITICAL else "⚠"
                color = "red" if check.severity == Severity.CRITICAL else "yellow"
                console.print(f"  [{color}]{icon} {check.name}[/{color}]: {check.message}")
                if check.details:
                    console.print(f"    [dim]{check.details}[/dim]")

        # Output JSON
        output_json = result.to_dict()
        console.print(f"\n[dim]Full validation result:[/dim]")
        console.print(json.dumps(output_json, indent=2))

        # Exit with appropriate code
        if result.is_critical():
            sys.exit(2)  # Critical failure
        elif result.has_warnings():
            sys.exit(1)  # Warnings
        else:
            sys.exit(0)  # Pass

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(2)


@app.command(name="validate-company")
def validate_company_cmd(
    company_name: str = typer.Argument(..., help="Company name to validate"),
    video_title: str = typer.Argument(..., help="Video title for context"),
    confidence: float = typer.Option(1.0, "--confidence", "-c", help="Extraction confidence score (0.0-1.0)"),
):
    """Validate extracted company name."""
    try:
        console.print(f"[cyan]Validating company name:[/cyan] {company_name}")

        result = validate_company_name_fn(company_name, video_title, confidence)

        # Display result
        console.print(f"\n[bold]Validation Status:[/bold] {result.status.value}")

        if result.is_critical():
            console.print("\n[red bold]CRITICAL ERRORS:[/red bold]")
        elif result.has_warnings():
            console.print("\n[yellow bold]WARNINGS:[/yellow bold]")
        else:
            console.print("\n[green bold]ALL CHECKS PASSED[/green bold]")

        # Display checks
        for check in result.checks:
            if not check.passed:
                icon = "✗" if check.severity == Severity.CRITICAL else "⚠"
                color = "red" if check.severity == Severity.CRITICAL else "yellow"
                console.print(f"  [{color}]{icon} {check.name}[/{color}]: {check.message}")

        # Output JSON
        console.print(f"\n[dim]Full validation result:[/dim]")
        console.print(json.dumps(result.to_dict(), indent=2))

        # Exit with appropriate code
        if result.is_critical():
            sys.exit(2)
        elif result.has_warnings():
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(2)


@app.command(name="validate-analysis")
def validate_analysis_cmd(
    analysis: Path = typer.Argument(..., help="Transcript analysis JSON file"),
):
    """Validate transcript analysis output."""
    try:
        console.print(f"[cyan]Validating analysis from:[/cyan] {analysis}")

        # Load analysis
        with open(analysis, "r", encoding="utf-8") as f:
            data = json.load(f)

        result = validate_analysis_fn(data)

        # Display result
        console.print(f"\n[bold]Validation Status:[/bold] {result.status.value}")

        if result.is_critical():
            console.print("\n[red bold]CRITICAL ERRORS:[/red bold]")
        elif result.has_warnings():
            console.print("\n[yellow bold]WARNINGS:[/yellow bold]")
        else:
            console.print("\n[green bold]ALL CHECKS PASSED[/green bold]")

        # Display checks
        for check in result.checks:
            if not check.passed:
                icon = "✗" if check.severity == Severity.CRITICAL else "⚠"
                color = "red" if check.severity == Severity.CRITICAL else "yellow"
                console.print(f"  [{color}]{icon} {check.name}[/{color}]: {check.message}")

        # Output JSON
        console.print(f"\n[dim]Full validation result:[/dim]")
        console.print(json.dumps(result.to_dict(), indent=2))

        # Exit with appropriate code
        if result.is_critical():
            sys.exit(2)
        elif result.has_warnings():
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(2)


@app.command(name="validate-metrics")
def validate_metrics_cmd(
    sections: Path = typer.Argument(..., help="Generated sections JSON file"),
    video_data: Path = typer.Argument(..., help="Video data JSON file"),
    analysis: Path = typer.Argument(..., help="Analysis JSON file"),
):
    """Validate metrics in generated content against transcript."""
    try:
        console.print("[cyan]Validating metrics for fabrication...[/cyan]")

        # Load files
        with open(sections, "r", encoding="utf-8") as f:
            sections_data = json.load(f)
        with open(video_data, "r", encoding="utf-8") as f:
            video_data_json = json.load(f)
        with open(analysis, "r", encoding="utf-8") as f:
            analysis_data = json.load(f)

        result = validate_metrics_fn(sections_data, video_data_json.get("transcript", ""), analysis_data)

        # Display result
        console.print(f"\n[bold]Validation Status:[/bold] {result.status.value}")

        if result.has_warnings():
            console.print("\n[yellow bold]WARNINGS:[/yellow bold]")
        else:
            console.print("\n[green bold]ALL METRICS VERIFIED[/green bold]")

        # Display checks
        for check in result.checks:
            if not check.passed:
                console.print(f"  [yellow]⚠ {check.name}[/yellow]: {check.message}")
            else:
                console.print(f"  [green]✓ {check.name}[/green]: {check.message}")

        # Output JSON
        console.print(f"\n[dim]Full validation result:[/dim]")
        console.print(json.dumps(result.to_dict(), indent=2))

        # Exit with appropriate code
        if result.has_warnings():
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(2)


@app.command(name="validate-consistency")
def validate_consistency_cmd(
    sections: Path = typer.Argument(..., help="Generated sections JSON file"),
    video_data: Path = typer.Argument(..., help="Video data JSON file"),
    verification: Path = typer.Argument(..., help="Company verification JSON file"),
):
    """Validate company consistency to prevent wrong company attribution."""
    try:
        console.print("[cyan]Validating company consistency...[/cyan]")

        # Load files
        with open(sections, "r", encoding="utf-8") as f:
            sections_data = json.load(f)
        with open(video_data, "r", encoding="utf-8") as f:
            video_data_json = json.load(f)
        with open(verification, "r", encoding="utf-8") as f:
            verification_data = json.load(f)

        expected_company = verification_data.get("matched_name", verification_data.get("query_name", "Unknown"))

        result = validate_company_consistency_fn(expected_company, sections_data, video_data_json)

        # Display result
        console.print(f"\n[bold]Validation Status:[/bold] {result.status.value}")

        if result.is_critical():
            console.print("\n[red bold]CRITICAL: COMPANY MISMATCH DETECTED![/red bold]")
            console.print("[red]This could be the Spotify hallucination bug![/red]")
        elif result.has_warnings():
            console.print("\n[yellow bold]WARNINGS:[/yellow bold]")
        else:
            console.print("\n[green bold]COMPANY CONSISTENCY VERIFIED[/green bold]")

        # Display checks
        for check in result.checks:
            if not check.passed:
                icon = "✗" if check.severity == Severity.CRITICAL else "⚠"
                color = "red" if check.severity == Severity.CRITICAL else "yellow"
                console.print(f"  [{color}]{icon} {check.name}[/{color}]: {check.message}")
                if check.details:
                    console.print(f"    [dim]{check.details}[/dim]")

        # Output JSON
        console.print(f"\n[dim]Full validation result:[/dim]")
        console.print(json.dumps(result.to_dict(), indent=2))

        # Exit with appropriate code
        if result.is_critical():
            sys.exit(2)
        elif result.has_warnings():
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(2)


@app.command(name="validate-all")
def validate_all_cmd(
    video_data: Path = typer.Argument(..., help="Video data JSON file"),
    analysis: Path = typer.Argument(..., help="Analysis JSON file"),
    sections: Path = typer.Argument(..., help="Sections JSON file"),
    verification: Path = typer.Argument(..., help="Verification JSON file"),
):
    """Run all validations comprehensively."""
    try:
        console.print("[cyan bold]Running comprehensive validation...[/cyan bold]\n")

        all_results = {}
        has_critical = False
        has_warnings = False

        # 1. Validate transcript
        console.print("[cyan]1. Validating transcript...[/cyan]")
        with open(video_data, "r", encoding="utf-8") as f:
            video_data_json = json.load(f)
        transcript_result = validate_transcript_fn(
            video_data_json.get("transcript", ""),
            video_data_json.get("transcript_segments", []),
        )
        all_results["transcript"] = transcript_result.to_dict()
        console.print(f"   Status: {transcript_result.status.value}\n")
        if transcript_result.is_critical():
            has_critical = True
        elif transcript_result.has_warnings():
            has_warnings = True

        # 2. Validate analysis
        console.print("[cyan]2. Validating analysis...[/cyan]")
        with open(analysis, "r", encoding="utf-8") as f:
            analysis_data = json.load(f)
        analysis_result = validate_analysis_fn(analysis_data)
        all_results["analysis"] = analysis_result.to_dict()
        console.print(f"   Status: {analysis_result.status.value}\n")
        if analysis_result.is_critical():
            has_critical = True
        elif analysis_result.has_warnings():
            has_warnings = True

        # 3. Validate metrics
        console.print("[cyan]3. Validating metrics...[/cyan]")
        with open(sections, "r", encoding="utf-8") as f:
            sections_data = json.load(f)
        metrics_result = validate_metrics_fn(sections_data, video_data_json.get("transcript", ""), analysis_data)
        all_results["metrics"] = metrics_result.to_dict()
        console.print(f"   Status: {metrics_result.status.value}\n")
        if metrics_result.has_warnings():
            has_warnings = True

        # 4. Validate company consistency
        console.print("[cyan]4. Validating company consistency...[/cyan]")
        with open(verification, "r", encoding="utf-8") as f:
            verification_data = json.load(f)
        expected_company = verification_data.get("matched_name", verification_data.get("query_name", "Unknown"))
        consistency_result = validate_company_consistency_fn(expected_company, sections_data, video_data_json)
        all_results["consistency"] = consistency_result.to_dict()
        console.print(f"   Status: {consistency_result.status.value}\n")
        if consistency_result.is_critical():
            has_critical = True
        elif consistency_result.has_warnings():
            has_warnings = True

        # Summary
        console.print("[bold]VALIDATION SUMMARY[/bold]")
        console.print("=" * 50)
        if has_critical:
            console.print("[red bold]❌ CRITICAL FAILURES DETECTED[/red bold]")
            console.print("[red]Workflow should STOP immediately[/red]")
        elif has_warnings:
            console.print("[yellow bold]⚠️  WARNINGS DETECTED[/yellow bold]")
            console.print("[yellow]Case study quality may be degraded[/yellow]")
        else:
            console.print("[green bold]✅ ALL VALIDATIONS PASSED[/green bold]")

        # Output full JSON
        console.print(f"\n[dim]Full validation results:[/dim]")
        console.print(json.dumps(all_results, indent=2))

        # Exit with appropriate code
        if has_critical:
            sys.exit(2)
        elif has_warnings:
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(2)


@app.command(name="validate-deep-analysis")
def validate_deep_analysis_cmd(
    analysis: Path = typer.Argument(..., help="Deep analysis JSON file"),
):
    """Validate deep analysis output for reference architectures."""
    exit_code = validate_deep_analysis_main(str(analysis))
    sys.exit(exit_code)


@app.command(name="validate-reference-architecture")
def validate_reference_architecture_cmd(
    ref_arch: Path = typer.Argument(..., help="Reference architecture JSON file"),
):
    """Validate reference architecture with technical depth scoring."""
    exit_code = validate_reference_architecture_main(str(ref_arch))
    sys.exit(exit_code)


@app.command(name="assemble-reference-architecture")
def assemble_reference_architecture_cmd(
    ref_arch_json: Path = typer.Argument(..., help="Reference architecture JSON file"),
    output: Path = typer.Argument(..., help="Output markdown file path"),
):
    """Assemble reference architecture markdown from JSON."""
    exit_code = assemble_reference_architecture_main(str(ref_arch_json), str(output))
    sys.exit(exit_code)


@app.command(name="fetch-github-profile")
def fetch_github_profile_cmd(
    username: str = typer.Argument(..., help="GitHub username"),
    output: Path = typer.Option(Path("github_profile.json"), "--output", "-o", help="Output JSON file path"),
):
    """Fetch GitHub profile data for a presenter."""
    try:
        console.print(f"[cyan]Fetching GitHub profile:[/cyan] {username}")
        profile = fetch_github_profile(username)

        # Write to file
        with open(output, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2)

        console.print(f"[green]✓ Profile data saved to:[/green] {output}")

        # Display profile info
        if profile.get("success"):
            console.print(f"[dim]Name:[/dim] {profile.get('name', 'N/A')}")
            console.print(f"[dim]Bio:[/dim] {profile.get('bio', 'N/A')}")
            console.print(f"[dim]Company:[/dim] {profile.get('company', 'N/A')}")
            console.print(f"[dim]Public repos:[/dim] {profile.get('public_repos', 0)}")

            # Display completeness score
            completeness = get_profile_completeness(profile)
            score_pct = completeness["score"] * 100
            color = "green" if completeness["score"] >= 0.7 else "yellow" if completeness["score"] >= 0.4 else "red"
            console.print(f"[{color}]Profile completeness:[/{color}] {score_pct:.0f}%")
        else:
            console.print(f"[red]✗ Failed to fetch profile[/red]")
            console.print(f"[red]Error:[/red] {profile.get('error', 'Unknown error')}")
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command(name="fetch-multi-video")
def fetch_multi_video_cmd(
    urls: List[str] = typer.Argument(..., help="YouTube video URLs (space-separated)"),
    output: Path = typer.Option(Path("videos_data.json"), "--output", "-o", help="Output JSON file path"),
):
    """Fetch data from multiple YouTube videos."""
    try:
        console.print(f"[cyan]Fetching data from {len(urls)} video(s)...[/cyan]")
        result = fetch_multi_video_data(urls)

        # Write to file
        with open(output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        console.print(f"[green]✓ Multi-video data saved to:[/green] {output}")

        # Display summary
        console.print(f"[dim]Total videos:[/dim] {result['total_videos']}")
        console.print(f"[dim]Successful:[/dim] {result['successful']}")
        console.print(f"[dim]Failed:[/dim] {result['failed']}")

        if result["failed"] > 0:
            console.print("\n[yellow]Failed videos:[/yellow]")
            for video in result["videos"]:
                if not video.get("success"):
                    console.print(f"  [red]✗[/red] {video.get('url', 'Unknown URL')}")
                    console.print(f"    [red]Error:[/red] {video.get('error', 'Unknown error')}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command(name="validate-presenter")
def validate_presenter_cmd(
    presenter_name: str = typer.Argument(..., help="Presenter name to validate"),
    videos_data: Path = typer.Argument(..., help="Multi-video data JSON file"),
):
    """Validate presenter name across multiple videos."""
    try:
        console.print(f"[cyan]Validating presenter:[/cyan] {presenter_name}")

        # Load videos data
        with open(videos_data, "r", encoding="utf-8") as f:
            data = json.load(f)

        result = validate_presenter(presenter_name, data)

        # Display result
        console.print(f"\n[bold]Validation Status:[/bold] {result.status.value}")

        if result.is_critical():
            console.print("\n[red bold]CRITICAL ERRORS:[/red bold]")
        elif result.has_warnings():
            console.print("\n[yellow bold]WARNINGS:[/yellow bold]")
        else:
            console.print("\n[green bold]ALL CHECKS PASSED[/green bold]")

        # Display checks
        for check in result.checks:
            if not check.passed:
                icon = "✗" if check.severity == Severity.CRITICAL else "⚠"
                color = "red" if check.severity == Severity.CRITICAL else "yellow"
                console.print(f"  [{color}]{icon} {check.name}[/{color}]: {check.message}")
                if check.details:
                    console.print(f"    [dim]{check.details}[/dim]")

        # Output JSON
        console.print(f"\n[dim]Full validation result:[/dim]")
        console.print(json.dumps(result.to_dict(), indent=2))

        # Exit with appropriate code
        if result.is_critical():
            sys.exit(2)
        elif result.has_warnings():
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(2)


@app.command(name="validate-biography")
def validate_biography_cmd(
    biography: Path = typer.Argument(..., help="Biography JSON file"),
):
    """Validate generated biography quality."""
    try:
        console.print(f"[cyan]Validating biography from:[/cyan] {biography}")

        # Load biography
        with open(biography, "r", encoding="utf-8") as f:
            data = json.load(f)

        result = validate_biography(data)

        # Display result
        console.print(f"\n[bold]Validation Status:[/bold] {result.status.value}")

        if result.is_critical():
            console.print("\n[red bold]CRITICAL ERRORS:[/red bold]")
        elif result.has_warnings():
            console.print("\n[yellow bold]WARNINGS:[/yellow bold]")
        else:
            console.print("\n[green bold]ALL CHECKS PASSED[/green bold]")

        # Display checks
        for check in result.checks:
            if not check.passed:
                icon = "✗" if check.severity == Severity.CRITICAL else "⚠"
                color = "red" if check.severity == Severity.CRITICAL else "yellow"
                console.print(f"  [{color}]{icon} {check.name}[/{color}]: {check.message}")
                if check.details:
                    console.print(f"    [dim]{check.details}[/dim]")

        # Output JSON
        console.print(f"\n[dim]Full validation result:[/dim]")
        console.print(json.dumps(result.to_dict(), indent=2))

        # Exit with appropriate code
        if result.is_critical():
            sys.exit(2)
        elif result.has_warnings():
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(2)


@app.command(name="validate-profile-update")
def validate_profile_update_cmd(
    existing_profile: Path = typer.Argument(..., help="Existing profile JSON file"),
    new_videos: Path = typer.Argument(..., help="New videos data JSON file"),
):
    """Validate profile update for consistency."""
    try:
        console.print("[cyan]Validating profile update...[/cyan]")

        # Load files
        with open(existing_profile, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
        with open(new_videos, "r", encoding="utf-8") as f:
            new_data = json.load(f)

        result = validate_profile_update(existing_data, new_data)

        # Display result
        console.print(f"\n[bold]Validation Status:[/bold] {result.status.value}")

        if result.is_critical():
            console.print("\n[red bold]CRITICAL ERRORS:[/red bold]")
        elif result.has_warnings():
            console.print("\n[yellow bold]WARNINGS:[/yellow bold]")
        else:
            console.print("\n[green bold]ALL CHECKS PASSED[/green bold]")

        # Display checks
        for check in result.checks:
            if not check.passed:
                icon = "✗" if check.severity == Severity.CRITICAL else "⚠"
                color = "red" if check.severity == Severity.CRITICAL else "yellow"
                console.print(f"  [{color}]{icon} {check.name}[/{color}]: {check.message}")
                if check.details:
                    console.print(f"    [dim]{check.details}[/dim]")

        # Output JSON
        console.print(f"\n[dim]Full validation result:[/dim]")
        console.print(json.dumps(result.to_dict(), indent=2))

        # Exit with appropriate code
        if result.is_critical():
            sys.exit(2)
        elif result.has_warnings():
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(2)


@app.command(name="validate-presenter-profile")
def validate_presenter_profile_cmd(
    profile: Path = typer.Argument(..., help="Presenter profile JSON file"),
    threshold: float = typer.Option(0.60, "--threshold", "-t", help="Minimum quality score threshold"),
):
    """Validate presenter profile quality with multi-factor scoring."""
    try:
        console.print(f"[cyan]Validating presenter profile:[/cyan] {profile}")

        # Load profile
        with open(profile, "r", encoding="utf-8") as f:
            data = json.load(f)

        result = validate_presenter_profile(data, threshold)

        # Display result
        console.print(f"\n[bold]Validation Status:[/bold] {result.status.value}")

        if result.is_critical():
            console.print("\n[red bold]CRITICAL ERRORS:[/red bold]")
        elif result.has_warnings():
            console.print("\n[yellow bold]WARNINGS:[/yellow bold]")
        else:
            console.print("\n[green bold]ALL CHECKS PASSED[/green bold]")

        # Display checks
        for check in result.checks:
            if not check.passed:
                icon = "✗" if check.severity == Severity.CRITICAL else "⚠"
                color = "red" if check.severity == Severity.CRITICAL else "yellow"
                console.print(f"  [{color}]{icon} {check.name}[/{color}]: {check.message}")
                if check.details:
                    console.print(f"    [dim]{check.details}[/dim]")
            else:
                console.print(f"  [green]✓ {check.name}[/green]: {check.message}")

        # Output JSON
        console.print(f"\n[dim]Full validation result:[/dim]")
        console.print(json.dumps(result.to_dict(), indent=2))

        # Exit with appropriate code
        if result.is_critical():
            sys.exit(2)
        elif result.has_warnings():
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(2)


@app.command(name="assemble-presenter-profile")
def assemble_presenter_profile_cmd(
    biography: Path = typer.Argument(..., help="Biography JSON file"),
    aggregation: Path = typer.Argument(..., help="Video aggregation JSON file"),
    sections: Path = typer.Argument(..., help="Sections JSON file"),
    existing_profile: Optional[Path] = typer.Option(
        None, "--existing-profile", "-e", help="Existing profile markdown file (for updates)"
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output markdown file path (auto-generated if not specified)"
    ),
):
    """Assemble presenter profile from component JSON files."""
    try:
        console.print("[cyan]Assembling presenter profile...[/cyan]")

        # Load JSON files
        with open(biography, "r", encoding="utf-8") as f:
            biography_data = json.load(f)
        with open(aggregation, "r", encoding="utf-8") as f:
            aggregation_data = json.load(f)
        with open(sections, "r", encoding="utf-8") as f:
            sections_data = json.load(f)

        result = assemble_presenter_profile(
            biography_data=biography_data,
            aggregation_data=aggregation_data,
            sections_data=sections_data,
            existing_profile_path=existing_profile,
            output_path=output,
        )

        console.print(f"[green]✓ Profile assembled:[/green] {result['output_path']}")
        console.print(f"[dim]Presenter:[/dim] {result['presenter_name']} (@{result['github_username']})")
        console.print(f"[dim]Version:[/dim] {result['profile_version']}")
        console.print(f"[dim]Metadata:[/dim] {result['metadata_path']}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        import traceback

        console.print(f"[red]{traceback.format_exc()}[/red]")
        sys.exit(2)


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
