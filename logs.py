import logging


def start_logging(firehose_filename, web_log_filename, debug):
    _format = '%(asctime)-15s %(levelname)-10s %(name)-11s %(message)s'
    date_format = '%Y-%m-%d %H:%M'
    log_level = logging.DEBUG

    # add the custom levels
    logging.addLevelName(22, 'MINIMAL')
    logging.addLevelName(26, 'SHORT')


    # Firehose
    logging.basicConfig(
        level=log_level,
        format=_format,
        datefmt=date_format,
        filename=firehose_filename,
        filemode='a'
    )

    if not debug:
        log_level = logging.CRITICAL

    # web file
    web_formatter = logging.Formatter(_format, date_format)
    web = logging.FileHandler(web_log_filename)
    web.setLevel(logging.CRITICAL)
    web.setFormatter(web_formatter)
    logging.getLogger().addHandler(web)

    # console
    console_formatter = logging.Formatter(_format, date_format)
    console = logging.StreamHandler()  # define a Handler that outputs to the console
    console.setLevel(log_level)
    console.setFormatter(console_formatter)
    logging.getLogger().addHandler(console)  # attach to the root logger

