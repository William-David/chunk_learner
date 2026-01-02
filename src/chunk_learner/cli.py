"""CLI interface for chunk learner."""

import typer
from rich.console import Console
from rich.table import Table
from typing import Optional
from . import database, operations

app = typer.Typer(help="Chunk Learner - Manage your learning journey in bite-sized pieces")
console = Console()


@app.command()
def init():
    """Initialize the database."""
    if database.database_exists():
        console.print("[yellow]Database already exists![/yellow]")
        return
    
    database.init_database()
    console.print("[green]✓[/green] Database initialized successfully!")
    console.print(f"Database location: {database.DB_PATH}")


@app.command()
def add():
    """Add a new learning chunk interactively."""
    if not database.database_exists():
        console.print("[red]Error:[/red] Database not initialized. Run 'chunk-learner init' first.")
        raise typer.Exit(1)
    
    console.print("\n[bold]Create a new learning chunk[/bold]\n")
    
    name = typer.prompt("Chunk name")
    description = typer.prompt("Description")
    difficulty = typer.prompt("Difficulty (1-5)", type=int)
    
    # Validate difficulty
    if difficulty < 1 or difficulty > 5:
        console.print("[red]Error:[/red] Difficulty must be between 1 and 5")
        raise typer.Exit(1)
    
    chunk_id = operations.create_chunk(name, description, difficulty)
    console.print(f"\n[green]✓[/green] Created chunk #{chunk_id}: {name}")
    
    # Ask about dependencies
    add_deps = typer.confirm("\nDoes this chunk depend on any other chunks?", default=False)
    
    if add_deps:
        # Show available chunks
        chunks = operations.get_all_chunks()
        if len(chunks) <= 1:  # Only the one we just created
            console.print("[yellow]No other chunks available yet![/yellow]")
        else:
            console.print("\n[bold]Available chunks:[/bold]")
            for chunk in chunks:
                if chunk.id != chunk_id:
                    console.print(f"  {chunk.id}: {chunk.name}")
            
            dep_ids = typer.prompt("\nEnter dependency chunk IDs (comma-separated)", default="")
            if dep_ids:
                for dep_id_str in dep_ids.split(","):
                    try:
                        dep_id = int(dep_id_str.strip())
                        if operations.add_dependency(chunk_id, dep_id):
                            console.print(f"[green]✓[/green] Added dependency on chunk #{dep_id}")
                        else:
                            console.print(f"[red]✗[/red] Failed to add dependency on chunk #{dep_id}")
                    except ValueError:
                        console.print(f"[red]✗[/red] Invalid chunk ID: {dep_id_str}")


@app.command()
def list():
    """List all learning chunks."""
    if not database.database_exists():
        console.print("[red]Error:[/red] Database not initialized. Run 'chunk-learner init' first.")
        raise typer.Exit(1)
    
    chunks = operations.get_all_chunks()
    
    if not chunks:
        console.print("[yellow]No chunks yet! Use 'chunk-learner add' to create one.[/yellow]")
        return
    
    table = Table(title="Learning Chunks")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="bold")
    table.add_column("Difficulty", style="yellow")
    table.add_column("Status", style="green")
    table.add_column("Dependencies")
    
    for chunk in chunks:
        status = "✓ Complete" if chunk.completed else "○ Incomplete"
        status_style = "green" if chunk.completed else "white"
        
        # Get dependencies
        deps = operations.get_chunk_dependencies(chunk.id)
        dep_text = ", ".join([f"#{d.id}" for d in deps]) if deps else "-"
        
        table.add_row(
            str(chunk.id),
            chunk.name,
            "★" * chunk.difficulty,
            f"[{status_style}]{status}[/{status_style}]",
            dep_text
        )
    
    console.print(table)


@app.command()
def complete(chunk_id: int):
    """Mark a chunk as completed.
    
    Args:
        chunk_id: ID of the chunk to complete
    """
    if not database.database_exists():
        console.print("[red]Error:[/red] Database not initialized. Run 'chunk-learner init' first.")
        raise typer.Exit(1)
    
    chunk = operations.get_chunk_by_id(chunk_id)
    
    if not chunk:
        console.print(f"[red]Error:[/red] Chunk #{chunk_id} not found")
        raise typer.Exit(1)
    
    if chunk.completed:
        console.print(f"[yellow]Chunk #{chunk_id} is already completed![/yellow]")
        return
    
    # Check if dependencies are met
    deps = operations.get_chunk_dependencies(chunk_id)
    incomplete_deps = [d for d in deps if not d.completed]
    
    if incomplete_deps:
        console.print(f"[red]Error:[/red] Cannot complete chunk #{chunk_id}. Incomplete dependencies:")
        for dep in incomplete_deps:
            console.print(f"  - #{dep.id}: {dep.name}")
        raise typer.Exit(1)
    
    if operations.complete_chunk(chunk_id):
        console.print(f"[green]✓[/green] Completed chunk #{chunk_id}: {chunk.name}")
    else:
        console.print(f"[red]Error:[/red] Failed to complete chunk #{chunk_id}")


@app.command()
def next():
    """Show the next chunk you should work on."""
    if not database.database_exists():
        console.print("[red]Error:[/red] Database not initialized. Run 'chunk-learner init' first.")
        raise typer.Exit(1)
    
    chunk = operations.get_next_available_chunk()
    
    if not chunk:
        console.print("[green]🎉 No chunks available! Either you're done or all chunks are blocked by dependencies.[/green]")
        return
    
    console.print("\n[bold]Next chunk to work on:[/bold]\n")
    console.print(f"[cyan]#{chunk.id}[/cyan] [bold]{chunk.name}[/bold]")
    console.print(f"Difficulty: {'★' * chunk.difficulty}")
    console.print(f"\n{chunk.description}\n")
    
    # Show dependencies if any
    deps = operations.get_chunk_dependencies(chunk.id)
    if deps:
        console.print("[dim]Dependencies (all completed):[/dim]")
        for dep in deps:
            console.print(f"  [green]✓[/green] #{dep.id}: {dep.name}")


if __name__ == "__main__":
    app()
