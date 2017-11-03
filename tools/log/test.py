from tools.log import logger_model

logger = logger_model.get_logger()
logger1 = logger_model.get_logger('console')

logger1.info("It debug!!!")
logger.debug("It info!!")
logger.info("It works!!!")
# logger.warning("It warning!!!")
# logger.error("It error!!!")
# logger.critical("It critical!!!")