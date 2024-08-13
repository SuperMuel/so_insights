from shared.models import Workspace

import logging

logger = logging.getLogger(__name__)


class Analyzer:
    def __init__(self):
        pass

    async def analyse(self, workspace: Workspace):
        logger.info(f"Analyzing workspace '{workspace.name}'")
        # Here we would do some analysis
        pass
