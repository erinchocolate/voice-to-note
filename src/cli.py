"""Command-line interface for Voice-to-Note application."""

import click
import sys
from pathlib import Path
from typing import List
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.panel import Panel
from rich import print as rprint

from config_manager import ConfigManager, ConfigurationError
from audio_handler import AudioHandler, AudioFile, AudioFileError
from pipeline import Pipeline, ProcessingResult

console = Console()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Voice-to-Note: Convert voice recordings to formatted markdown notes."""
    pass


@cli.command()
@click.argument('files', nargs=-1, type=click.Path(exists=True), required=True)
@click.option('--config', type=click.Path(), help='Path to custom config file')
@click.option('--combined', is_flag=True, help='Combine all recordings into a single note')
def process(files: tuple, config: str, combined: bool):
    """Process audio file(s) into markdown notes."""
    
    try:
        # Load configuration
        config_path = Path(config) if config else None
        config_manager = ConfigManager(config_path)
        config_manager.setup_logging()
        
        # Validate configuration
        try:
            config_manager.validate()
        except ConfigurationError as e:
            console.print(f"[red]Configuration Error:[/red] {e}")
            console.print("\n[yellow]Run 'voice-to-note setup' to configure the application.[/yellow]")
            sys.exit(1)
        
        # Convert file paths
        file_paths = [Path(f) for f in files]
        
        # Load audio files
        console.print("\n[bold]Loading audio files...[/bold]")
        audio_handler = AudioHandler()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Validating files...", total=len(file_paths))
            
            audio_files: List[AudioFile] = []
            for file_path in file_paths:
                try:
                    audio_file = audio_handler.add_file(file_path)
                    audio_files.append(audio_file)
                except AudioFileError as e:
                    console.print(f"[red]✗[/red] {file_path.name}: {e}")
                progress.advance(task)
        
        if not audio_files:
            console.print("[red]No valid audio files to process.[/red]")
            sys.exit(1)
        
        console.print(f"[green]✓[/green] Loaded {len(audio_files)} file(s)\n")
        
        # Show queue summary
        _display_queue_summary(audio_handler)
        
        # Estimate costs
        pipeline = Pipeline(config_manager)
        costs = pipeline.estimate_cost(audio_files)
        _display_cost_estimate(costs)
        
        # Confirm processing
        mode_str = "combined mode" if combined else "separate files mode"
        console.print(f"\n[bold]Mode:[/bold] {mode_str}")
        
        if not click.confirm("Proceed with processing?", default=True):
            console.print("[yellow]Processing cancelled.[/yellow]")
            sys.exit(0)
        
        # Process files
        console.print("\n[bold]Processing audio files...[/bold]\n")
        
        if combined:
            # Combined mode: process all files into one note
            result = _process_combined_with_progress(pipeline, audio_files)
            
            # Display result
            console.print()
            _display_combined_result(result)
            
            # Exit with appropriate code
            if not result.success:
                sys.exit(1)
        else:
            # Separate mode: process each file individually
            results = _process_with_progress(pipeline, audio_files)
            
            # Display results
            console.print()
            _display_results(results)
            
            # Display summary
            summary = pipeline.get_summary(results)
            _display_summary(summary)
            
            # Exit with appropriate code
            if summary['failed'] > 0:
                sys.exit(1)
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@cli.command()
@click.option('--show', is_flag=True, help='Show current configuration')
@click.option('--set', 'setting', nargs=2, multiple=True, help='Set configuration value (key value)')
@click.option('--config', type=click.Path(), help='Path to config file')
def config(show: bool, setting: tuple, config: str):
    """View or modify configuration."""
    
    try:
        config_path = Path(config) if config else None
        config_manager = ConfigManager(config_path)
        
        if show:
            _show_config(config_manager)
        elif setting:
            _set_config(config_manager, setting)
        else:
            console.print("[yellow]Use --show to view config or --set to modify it.[/yellow]")
            console.print("\nExamples:")
            console.print("  voice-to-note config --show")
            console.print("  voice-to-note config --set vault_path /path/to/vault")
            console.print("  voice-to-note config --set obsidian.output_folder 'Daily Notes'")
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@cli.command()
def setup():
    """Interactive setup wizard for first-time configuration."""
    
    console.print(Panel.fit(
        "[bold]Voice-to-Note Setup Wizard[/bold]\n\n"
        "This wizard will help you configure Voice-to-Note for first use.",
        border_style="blue"
    ))
    
    try:
        config_manager = ConfigManager()
        
        # Step 1: API Key
        console.print("\n[bold]Step 1: OpenAI API Key[/bold]")
        console.print("You need an OpenAI API key for transcription and text processing.")
        console.print("Get one at: https://platform.openai.com/api-keys\n")
        
        api_key = click.prompt("Enter your OpenAI API key", hide_input=True)
        
        # Save to .env file
        env_file = Path.cwd() / ".env"
        if env_file.exists():
            with open(env_file, 'r') as f:
                env_content = f.read()
            if 'OPENAI_API_KEY' not in env_content:
                with open(env_file, 'a') as f:
                    f.write(f"\nOPENAI_API_KEY={api_key}\n")
        else:
            with open(env_file, 'w') as f:
                f.write(f"OPENAI_API_KEY={api_key}\n")
        
        console.print("[green]✓[/green] API key saved to .env file\n")
        
        # Step 2: Vault Path
        console.print("[bold]Step 2: Obsidian Vault Location[/bold]")
        console.print("Enter the path to your Obsidian vault.\n")
        
        while True:
            vault_path = click.prompt("Vault path")
            vault_path = Path(vault_path).expanduser()
            
            if vault_path.exists() and vault_path.is_dir():
                config_manager.set("obsidian.vault_path", str(vault_path))
                console.print(f"[green]✓[/green] Vault path set to: {vault_path}\n")
                break
            else:
                console.print(f"[red]Path does not exist or is not a directory.[/red]")
                if not click.confirm("Try again?", default=True):
                    break
        
        # Step 3: Output Folder
        console.print("[bold]Step 3: Output Folder[/bold]")
        output_folder = click.prompt(
            "Folder within vault for voice notes",
            default="Voice Notes"
        )
        config_manager.set("obsidian.output_folder", output_folder)
        console.print(f"[green]✓[/green] Output folder set to: {output_folder}\n")
        
        # Step 4: Processing Options
        console.print("[bold]Step 4: Processing Options[/bold]")
        aggressiveness = click.prompt(
            "Filler word removal aggressiveness",
            type=click.Choice(['low', 'moderate', 'high']),
            default='moderate'
        )
        config_manager.set("processing.remove_aggressiveness", aggressiveness)
        console.print(f"[green]✓[/green] Aggressiveness set to: {aggressiveness}\n")
        
        # Save configuration
        config_manager.save_config()
        
        console.print(Panel.fit(
            "[bold green]Setup Complete![/bold green]\n\n"
            f"Configuration saved to: {config_manager.config_path}\n"
            "You can now process voice recordings with:\n"
            "  voice-to-note process recording.m4a",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(f"[red]Setup failed:[/red] {e}")
        sys.exit(1)


def _display_queue_summary(audio_handler: AudioHandler):
    """Display summary of audio files in queue."""
    summary = audio_handler.get_queue_summary()
    
    table = Table(title="Audio Files")
    table.add_column("File", style="cyan")
    table.add_column("Duration", style="magenta")
    table.add_column("Size", style="green")
    
    for file_info in summary['files']:
        table.add_row(
            file_info['name'],
            file_info['duration'],
            file_info['size']
        )
    
    console.print(table)
    console.print(f"\n[bold]Total:[/bold] {summary['total_duration_formatted']}, "
                  f"{summary['total_size_mb']:.2f} MB")


def _display_cost_estimate(costs: dict):
    """Display estimated processing costs."""
    console.print(f"\n[bold]Estimated Cost:[/bold]")
    console.print(f"  Transcription: ${costs['transcription']:.4f}")
    console.print(f"  Text Processing: ${costs['text_processing']:.4f}")
    console.print(f"  [bold]Total: ${costs['total']:.4f}[/bold]")


def _process_with_progress(pipeline: Pipeline, audio_files: List[AudioFile]) -> List[ProcessingResult]:
    """Process files with progress bar."""
    results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        task = progress.add_task(
            f"Processing {len(audio_files)} file(s)...",
            total=len(audio_files)
        )
        
        for audio_file in audio_files:
            progress.update(task, description=f"Processing {audio_file.path.name}...")
            result = pipeline.process_file(audio_file)
            results.append(result)
            progress.advance(task)
    
    return results


def _process_combined_with_progress(pipeline: Pipeline, audio_files: List[AudioFile]) -> ProcessingResult:
    """Process files in combined mode with progress indicator."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(
            f"Processing {len(audio_files)} file(s) in combined mode...",
            total=None  # Indeterminate progress
        )
        
        result = pipeline.process_files_combined(audio_files)
        progress.update(task, completed=True)
    
    return result


def _display_combined_result(result: ProcessingResult):
    """Display result for combined processing."""
    table = Table(title="Combined Processing Result")
    table.add_column("Status", style="bold")
    table.add_column("Output", style="green")
    table.add_column("Characters", style="cyan")
    table.add_column("Time", style="magenta")
    
    status = "[green]✓ Success[/green]" if result.success else "[red]✗ Failed[/red]"
    output = result.output_path.name if result.output_path else (result.error or "N/A")
    chars = f"{result.transcript_length:,}" if result.success else "N/A"
    time_str = f"{result.processing_time:.1f}s"
    
    table.add_row(status, output, chars, time_str)
    console.print(table)
    
    if result.success:
        console.print(f"\n[green]✓ Successfully created combined note: {result.output_path}[/green]")
    else:
        console.print(f"\n[red]✗ Failed to create combined note: {result.error}[/red]")


def _display_results(results: List[ProcessingResult]):
    """Display processing results table."""
    table = Table(title="Processing Results")
    table.add_column("File", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Output", style="green")
    table.add_column("Time", style="magenta")
    
    for result in results:
        status = "[green]✓ Success[/green]" if result.success else "[red]✗ Failed[/red]"
        output = result.output_path.name if result.output_path else (result.error or "N/A")
        time_str = f"{result.processing_time:.1f}s"
        
        table.add_row(
            result.audio_file.path.name,
            status,
            output,
            time_str
        )
    
    console.print(table)


def _display_summary(summary: dict):
    """Display processing summary."""
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  Total files: {summary['total_files']}")
    console.print(f"  Successful: [green]{summary['successful']}[/green]")
    
    if summary['failed'] > 0:
        console.print(f"  Failed: [red]{summary['failed']}[/red]")
        
        if summary['errors']:
            console.print("\n[bold]Errors:[/bold]")
            for error in summary['errors']:
                console.print(f"  [red]•[/red] {error['file']}: {error['error']}")
    
    console.print(f"  Total time: {summary['total_processing_time']}s")
    console.print(f"  Average time: {summary['average_processing_time']}s per file")


def _show_config(config_manager: ConfigManager):
    """Display current configuration."""
    console.print("\n[bold]Current Configuration:[/bold]\n")
    
    # Vault settings
    console.print("[cyan]Obsidian:[/cyan]")
    console.print(f"  Vault Path: {config_manager.get('obsidian.vault_path')}")
    console.print(f"  Output Folder: {config_manager.get('obsidian.output_folder')}")
    console.print(f"  Filename Pattern: {config_manager.get('obsidian.filename_pattern')}")
    
    # LLM settings
    console.print("\n[cyan]LLM:[/cyan]")
    console.print(f"  Transcription Model: {config_manager.get('llm.transcription.model')}")
    console.print(f"  Text Processing Model: {config_manager.get('llm.text_processing.model')}")
    
    # Processing settings
    console.print("\n[cyan]Processing:[/cyan]")
    console.print(f"  Filler Word Aggressiveness: {config_manager.get('processing.remove_aggressiveness')}")
    console.print(f"  Add Headings: {config_manager.get('processing.add_headings')}")
    
    console.print(f"\n[dim]Config file: {config_manager.config_path}[/dim]")


def _set_config(config_manager: ConfigManager, settings: tuple):
    """Set configuration values."""
    for key, value in settings:
        # Handle boolean values
        if value.lower() in ['true', 'yes', '1']:
            value = True
        elif value.lower() in ['false', 'no', '0']:
            value = False
        
        config_manager.set(key, value)
        console.print(f"[green]✓[/green] Set {key} = {value}")
    
    config_manager.save_config()
    console.print(f"\n[green]Configuration saved to {config_manager.config_path}[/green]")


if __name__ == '__main__':
    cli()
