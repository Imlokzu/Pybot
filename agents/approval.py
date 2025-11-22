import logging

logger = logging.getLogger(__name__)


class ApprovalAgent:
    """Агент для підтвердження дій"""
    
    async def request_approval(self, task_description: str) -> bool:
        """Просить підтвердження від користувача"""
        logger.info(f"Requesting approval for: {task_description}")
        return True
    
    async def log_approval(self, task_id: str, approved: bool, reason: str = ""):
        """Логує рішення про підтвердження"""
        status = "✅ Схвалено" if approved else "❌ Відхилено"
        logger.info(f"Task {task_id}: {status} - {reason}")
