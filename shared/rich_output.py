"""rich_output.py — Rich text formatting for all red-hot_rebis CLI output.

Provides styled print functions using the `rich` library.
Uses force_terminal=True so colors render even in piped/subprocess environments.
Set env NO_COLOR=1 for plain-text fallback.


Color scheme:
  Target/Product      bold green
  SMILES              cyan
  Section headers     bold yellow on blue bar
  Separators          bright blue
  δ / numeric values  bold yellow
  Bond names          bold magenta
  FGs                 bold blue
  Precursors          green
  Success/Found       bold green
  Errors              bold red
  CAS/metadata        dim white
  Analogs             yellow
  Step numbers        bold cyan
"""

from shared.rich_output import *
import os

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.columns import Columns
from rich.layout import Layout
from rich.rule import Rule

# ── Console setup ─────────────────────────────────────────────────────
# force_terminal=True ensures colors render even when stdout is piped
# or running in a subprocess. NO_COLOR env var disables coloring.
_no_color = os.environ.get("NO_COLOR", "").strip().lower() in ("1", "true", "yes")
_console = Console(force_terminal=not _no_color, color_system="truecolor" if not _no_color else None)
STYLED = not _no_color  # set False for plain output


# ── Styled Print Helpers ──────────────────────────────────────────────

def cprint(*args, style=None, **kwargs):
    """Rich-conditional print: uses rich if STYLED, plain print otherwise."""
    if STYLED:
        kwargs.pop("end", _console)
        _console.print(*args, style=style, **kwargs)
    else:
        print(*args, **kwargs)

def header(title, width=66):
    """Print a styled section header with decorative bar."""
    if STYLED:
        _console.rule(f"[bold yellow]{title}[/bold yellow]", style="bright_blue")
    else:
        print("=" * width)
        info_line(f"  {title}")
        print("=" * width)

def subheader(title):
    """Print a smaller styled sub-header."""
    if STYLED:
        _console.print(f"\n[bold cyan]▸ {title}[/bold cyan]")
    else:
        info_line(f"\n  {title}")

def separator(width=66, char="─"):
    """Print a styled separator line."""
    if STYLED:
        _console.rule(style="bright_blue")
    else:
        print(char * width)

def target_line(name, smi="", indent=0):
    """Print a target molecule line with its SMILES."""
    pad = "  " * indent
    if STYLED:
        txt = Text()
        txt.append(f"{pad}", style="")
        txt.append(name, style="bold green")
        if smi:
            txt.append(f"  ", style="")
            txt.append(f"SMILES: {smi}", style="cyan")
        _console.print(txt)
    else:
        smi_str = f"  SMILES: {smi}" if smi else ""
        info_line(f"{pad}{name}  {smi_str}")

def precursor_line(label, name, fg_hint="", smi="", indent=0):
    """Print a precursor line."""
    pad = "  " * indent
    if STYLED:
        txt = Text()
        txt.append(f"{pad}{label}: ", style="")
        txt.append(name, style="green")
        if fg_hint:
            txt.append(f"  [{fg_hint}]", style="blue")
        if smi:
            txt.append(f"  ", style="")
            txt.append(f"SMILES: {smi}", style="cyan")
        _console.print(txt)
    else:
        smi_str = f"  SMILES: {smi}" if smi else ""
        fg_str = f"  [{fg_hint}]" if fg_hint else ""
        info_line(f"{pad}{label}: {name}{fg_str}  {smi_str}")

def bond_line(text, indent=0):
    """Print a bond description line (disconnection cut)."""
    pad = "  " * indent
    if STYLED:
        _console.print(f"{pad}{text}", style="bold magenta")
    else:
        info_line(f"{pad}{text}")

def numeric_line(label, value, unit="", indent=0):
    """Print a label with a highlighted numeric value."""
    pad = "  " * indent
    if STYLED:
        txt = Text()
        txt.append(f"{pad}{label}: ", style="")
        txt.append(str(value), style="bold yellow")
        if unit:
            txt.append(f" {unit}", style="")
        _console.print(txt)
    else:
        info_line(f"{pad}{label}: {value}" + (f" {unit}" if unit else ""))

def info_line(text, indent=0):
    """Print a metadata/info line in dim style."""
    pad = "  " * indent
    if STYLED:
        _console.print(f"{pad}{text}", style="dim white")
    else:
        info_line(f"{pad}{text}")

def fg_line(text, indent=0):
    """Print a functional group line in blue."""
    pad = "  " * indent
    if STYLED:
        _console.print(f"{pad}{text}", style="bold blue")
    else:
        info_line(f"{pad}{text}")

def success_line(text, indent=0):
    """Print a success/confirmation line in bold green."""
    pad = "  " * indent
    if STYLED:
        _console.print(f"{pad}{text}", style="bold green")
    else:
        info_line(f"{pad}{text}")



def warning_line(text, indent=0):
    """Print a warning line in bold yellow."""
    pad = "  " * indent
    if STYLED:
        _console.print(f"{pad}{text}", style="bold yellow")
    else:
        info_line(f"{pad}{text}")
def error_line(text, indent=0):
    """Print an error/warning line in bold red."""
    pad = "  " * indent
    if STYLED:
        _console.print(f"{pad}{text}", style="bold red")
    else:
        info_line(f"{pad}{text}")

def analog_line(name, dist, smi="", indent=0):
    """Print a structural analog line."""
    pad = "  " * indent
    if STYLED:
        txt = Text()
        txt.append(f"{pad}", style="")
        txt.append(f"{name:40s}", style="yellow")
        txt.append(f" d={dist:.3f}", style="bold yellow")
        if smi:
            txt.append(f"  ", style="")
            txt.append(f"SMILES: {smi}", style="cyan")
        _console.print(txt)
    else:
        smi_str = f"  SMILES: {smi}" if smi else ""
        info_line(f"  {name:40s} d={dist:.3f}  {smi_str}")

def path_step(step_num, label="", indent=0):
    """Print a path step header."""
    pad = "  " * indent
    if STYLED:
        _console.print(f"{pad}[bold cyan]Step {step_num}[/bold cyan]{' ' + label if label else ''}")
    else:
        info_line(f"{pad}Step {step_num}:{label}")

def step_detail(key, value, indent=1):
    """Print a key: value line within a step."""
    pad = "  " * indent
    if STYLED:
        _console.print(f"{pad}[dim]{key}:[/dim] [white]{value}[/white]")
    else:
        info_line(f"{pad}{key}: {value}")

def demo_title():
    """Print the startup title panel."""
    if STYLED:
        _console.print(Panel.fit(
            "[bold green]ch3mpiler[/bold green] — [yellow]Grammar-Derived Retrosynthetic Engine[/yellow]\n"
            "[dim]No named reactions — disconnections from 12-primitive rules[/dim]",
            border_style="bright_blue",
            padding=(1, 2)
        ))
    else:
        print("=" * 66)
        info_line("  ch3mpiler — Grammar-Derived Retrosynthetic Engine")
        info_line("  No named reactions — disconnections from 12-primitive rules")
        print("=" * 66)
def conflict_line(prim, tgt_val, src_val, indent=1):
    """Print a structural conflict report line."""
    pad = "  " * indent
    if STYLED:
        _console.print(
            f"{pad}[bold red]✗[/bold red] [bold]{prim}[/bold]: target=[yellow]{tgt_val}[/yellow] vs start=[yellow]{src_val}[/yellow]"
        )
    else:
        info_line(f"{pad}  {prim}: target={tgt_val} vs start={src_val}")


def table(headers, rows, title=None):
    """Print a styled rich Table."""
    if not STYLED:
        # Fallback: plain text table
        fmt = "  ".join(f"{h:>{len(h)}}" for h in headers)
        info_line(f"  {fmt}")
        info_line(f"  {'  '.join('-'*len(h) for h in headers)}")
        for row in rows:
            info_line(f"  {'  '.join(str(c) for c in row)}")
        return
    t = Table(title=title, box=box.ROUNDED, border_style="bright_blue",
              header_style="bold yellow", title_style="bold white")
    for h in headers:
        t.add_column(h)
    for row in rows:
        t.add_row(*[str(c) for c in row])
    _console.print(t)


def panel(title, content, style="bright_blue"):
    """Print a styled panel around content."""
    if STYLED:
        _console.print(Panel(content, title=title, border_style=style, padding=(1, 2)))
    else:
        info_line(f"--- {title} ---")
        print(content)
        info_line("---")

def step_product_line(product, smi="", indent=0):
    """Print a step product with green highlight."""
    pad = "  " * indent
    if STYLED:
        txt = Text()
        txt.append(f"{pad}Product:   ", style="")
        txt.append(product, style="bold green")
        if smi:
            txt.append(f"  ", style="")
            txt.append(f"SMILES: {smi}", style="cyan")
        _console.print(txt)
    else:
        smi_str = f"  SMILES: {smi}" if smi else ""
        info_line(f"{pad}Product:   {product}  {smi_str}")

def reaction_header(title, subtitle=""):
    """Print a large reaction/sub-reaction header panel."""
    if STYLED:
        content = f"[bold]{title}[/bold]"
        if subtitle:
            content += f"\n[dim]{subtitle}[/dim]"
        _console.print(Panel(content, border_style="bright_blue", padding=(1, 2)))
    else:
        print("=" * 66)
        info_line(f"  {title}")
        if subtitle:
            info_line(f"  {subtitle}")
        print("=" * 66)