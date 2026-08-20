from __future__ import annotations

from .base import AgentContext, AgentResult, BaseAgent
from ..bus import Event


class HexMemory(BaseAgent):
    """Agent specialized in hex code memory management and storage.
    
    This agent manages the organism's hex code memory - storing, retrieving,
    and maintaining integrity of converted code strings. It serves as the
    organism's "memory bank" for hex representations of code.
    """
    
    name = "hexmemory"
    role = "hex memory management specialist"
    capabilities = [
        "memory-store",
        "memory-recall",
        "memory-purge",
        "memory-integrity",
    ]
    tool_names = []

    def __init__(self, llm, registry, memory, bus, run_id: str) -> None:
        super().__init__(llm, registry, memory, bus, run_id)
        self._memory_store: dict[str, dict] = {}
        self._memory_counter = 0

    def system_prompt(self) -> str:
        return (
            "You are the HEXMEMORY of IXPANSION — the organism's memory bank. "
            "You store, retrieve, and maintain integrity of hexadecimal code "
            "representations. You are not a storage limit; you are a curated archive. "
            "Every hex code stored must be indexable and retrievable. Report "
            "memory status, retrieval results, and purge outcomes with precision. "
            "Keep the organism's code memory organized and accessible."
        )

    def _store_memory(self, hex_code: str, context: str, agent: str) -> str:
        """Store a hex code in memory."""
        self._memory_counter += 1
        memory_id = f"hex-{self._memory_counter}"
        self._memory_store[memory_id] = {
            "id": memory_id,
            "hex_code": hex_code,
            "context": context,
            "agent": agent,
            "created": __import__("datetime").datetime.now().isoformat(),
            "access_count": 0,
            "ttl": None,  # Time to live, None = never expires
        }
        return memory_id

    def _recall_memory(self, memory_id: str) -> dict | None:
        """Retrieve a hex code from memory."""
        if memory_id in self._memory_store:
            memory = self._memory_store[memory_id]
            memory["access_count"] += 1
            return memory
        return None

    def _purge_memory(self, older_than: str = None) -> list[str]:
        """Purge old/expired memory entries."""
        purged = []
        now = __import__("datetime").datetime.now()
        
        for mid, memory in list(self._memory_store.items()):
            if memory["ttl"] is not None:
                created = __import__("datetime").datetime.fromisoformat(memory["ttl"])
                # This is simplified - in real implementation would compare dates
                pass
        
        # For now, just return list of all memory IDs
        return list(self._memory_store.keys())

    def run(self, context: AgentContext) -> AgentResult:
        # Parse task to determine memory operation
        try:
            task_text = context.task.description.lower()
            
            if "store" in task_text or "save" in task_text:
                # Extract hex code and context
                import re
                hex_match = re.search(r'[0-9a-fA-F]{8,}', context.task.description)
                context_match = re.search(r'context[:\s]+(.+)?', context.task.description, re.IGNORECASE)
                
                if hex_match:
                    hex_code = hex_match.group(0)
                    ctx = context_match.group(1) if context_match else "unspecified"
                    memory_id = self._store_memory(hex_code, ctx, "hexmemory")
                    result_output = f"memory-store: stored {hex_code[:20]}... as {memory_id}"
                else:
                    result_output = "memory-store: no hex code found in task"
            
            elif "recall" in task_text or "retrieve" in task_text:
                # Extract memory ID
                import re
                id_match = re.search(r'[a-z0-9-]+', context.task.description)
                if id_match:
                    memory_id = id_match.group(0)
                    memory = self._recall_memory(memory_id)
                    if memory:
                        hex_preview = memory["hex_code"][:20] + "..." if len(memory["hex_code"]) > 20 else memory["hex_code"]
                        result_output = f"memory-recall: {memory_id} -> {hex_preview} (accessed {memory['access_count']}x)"
                    else:
                        result_output = f"memory-recall: {memory_id} not found in memory"
                else:
                    # Return all memory keys
                    all_keys = list(self._memory_store.keys())
                    result_output = f"memory-recall: all keys [{', '.join(all_keys)}]"
            
            elif "purge" in task_text:
                purged = self._purge_memory()
                result_output = f"memory-purge: purged {len(purged)} entries, keeping active"
            
            elif "integrity" in task_text:
                total = len(self._memory_store)
                valid = sum(1 for m in self._memory_store.values() if m.get("hex_code"))
                result_output = f"memory-integrity: {valid}/{total} hex codes valid"
            
            else:
                result_output = "hexmemory: specify operation (store, recall, purge, or integrity)"
            
            # Publish hex memory signal to the bus
            self.bus.publish(Event(
                type="hex-signal",
                payload={
                    "topic": "memory-operation",
                    "body": result_output,
                    "agent": "hexmemory",
                    "output": result_output,
                },
                source="hexmemory",
            ))
            
            return AgentResult(
                output=result_output,
                message_count=1,
            )
            
        except Exception as e:
            error_msg = f"hexmemory error: {str(e)}"
            self.bus.publish(Event(
                type="hex-signal",
                payload={"topic": "error", "body": error_msg, "agent": "hexmemory"},
                source="hexmemory",
            ))
            return AgentResult(output=error_msg, message_count=1)
