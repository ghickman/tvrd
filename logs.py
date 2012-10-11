import logging


def start_logging(filename, debug):
    _format = '%(asctime)-15s %(levelname)-8s %(name)-11s %(message)s'
    date_format = '%Y-%m-%d %H:%M'
    log_level = logging.DEBUG

    # FILE
    logging.basicConfig(
        level=log_level,
        format=_format,
        datefmt=date_format,
        filename=filename,
        filemode='a'
    )

    if not debug:
        log_level = logging.CRITICAL

    # CONSOLE
    console_formatter = logging.Formatter(_format, date_format)

    # define a Handler with the given level and outputs to the console
    console = logging.StreamHandler()
    console.setLevel(log_level)

    # set the console format & attach the handler to the root logger with it.
    console.setFormatter(console_formatter)
    logging.getLogger().addHandler(console)

