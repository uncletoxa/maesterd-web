import logging.config
import click
from dataclasses import dataclass

from maesterd.llm.graph import graph
from maesterd import config


def set_logging_configurations(log_level=logging.INFO):
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
        },
        "root": {
            "level": log_level,
            "handlers": ["console"],
        },
    }
    logging.config.dictConfig(log_config)


set_logging_configurations()


def _set_configs(configs):
    """
    Set multiple configuration key-value pairs.
    Usage: set-config key1=value1 key2=value2 ...
    """
    if not configs:
        return
    for item in configs:
        try:
            key, value = item.split("=", 1)
            if value.isdigit():
                value = int(value)
            elif value.lower() in ("true", "false"):
                value = value.lower() == "true"
            config.set(key, value)
            click.echo(f"Configuration '{key}' set to '{value}'.")
        except ValueError:
            click.echo(f"Invalid configuration format: '{item}'. Use key=value format.")
        except Exception as e:
            click.echo(f"Failed to set configuration '{item}': {e}")


@dataclass
class AppRunConfig:
    debug: bool
    recursion_limit: int


@click.group()
@click.option("--debug", is_flag=True, default=config.get("maesterd.graph.debug"), help="Enable debug mode.")
@click.option("--recursion-limit", default=config.get("maesterd.graph.recursion_limit"), help="Set recursion limit.")
@click.pass_context
def cli(context, debug, recursion_limit):
    """Main command group for campaign CLI."""
    context.obj = AppRunConfig(debug=debug, recursion_limit=recursion_limit)


@cli.command()
@click.argument("configs", nargs=-1)
def set_configs(configs):
    """
    Set configuration key-value pairs.
    """
    _set_configs(configs=configs)


@cli.command()
@click.option('--num-pc', default=1, help='Number of playable characters to create.')
@click.pass_obj
def run(conf, num_pc):
    """
    Run the campaign with the current configuration.

    Examples
    --------
        poetry run campaign run
        poetry run campaign run maesterd.graph.debug=true maesterd.graph.recursion_limit=30
    """
    graph.invoke(
        input={"messages": [], 'num_pc': num_pc},
        config={"recursion_limit": conf.recursion_limit},
        debug=False,
    )


@cli.command()
@click.option('--socket-path', default='/tmp/sockets/maesterd.sock',help='Unix socket path')
@click.option('--mock-response', is_flag=True, help='Mock response w/o a call to the LLM')
def serve(socket_path, mock_response):
    """
    Start the maesterd socket api.

    Example:
        poetry run campaign serve
        poetry run campaign serve --socket-path /custom/path/maesterd.sock --mock-response
    """
    from maesterd.api.server import run_server
    run_server(socket_path, mock_response=mock_response)


if __name__ == "__main__":
    cli()
