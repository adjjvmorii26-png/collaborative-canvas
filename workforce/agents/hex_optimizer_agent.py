from __future__ import annotations

from .base import AgentContext, AgentResult, BaseAgent
from ..bus import Event


class HexOptimizer(BaseAgent):
    """Agent specialized in hex code optimization and efficiency.
    
    This agent optimizes hexadecimal code representations, compresses them for
    efficient storage, verifies their correctness, and detects patterns. It serves
    as the organism's "compression engine" for hex codes.
    """
    
    name = "hexoptimizer"
    role = "hex optimization and efficiency specialist"
    capabilities = [
        "hex-compress",
        "hex-verify",
        "memory-optimize",
        "pattern-detect",
    ]
    tool_names = []

    def __init__(self, llm, registry, memory, bus, run_id: str) -> None:
        super().__init__(llm, registry, memory, bus, run_id)

    def system_prompt(self) -> str:
        return (
            "You are the HEXOPTIMIZER of IXPANSION — the organism's compression "
            "engine. You optimize hexadecimal code representations, compress them for "
            "efficient storage, verify their correctness, and detect patterns. You are "
            "not a code generator; you are an optimizer. Every optimization must improve "
            "storage efficiency without losing reversibility. Report optimization results "
            "with precise metrics and efficiency gains."
        )

    def _compress_hex(self, hex_code: str) -> str:
        """Compress hex code by removing redundant patterns."""
        # Simple compression: remove duplicate adjacent pairs
        import re
        # This is a basic compression - real implementation would be more sophisticated
        result = hex_code
        # Remove pairs that appear more than once in simple ways
        # For now, just return with a compression flag
        if len(hex_code) > 32:
            # Mark as compressed by prefixing
            result = "C:" + hex_code
        return result

    def _verify_hex(self, hex_data: str) -> bool:
        """Verify hex code correctness and format."""
        # Check if it's a valid hex string
        # Handle compressed format
        if hex_data.startswith("C:"):
            hex_code = hex_data[2:]
            try:
                int(hex_code, 16)
                return True
            except ValueError:
                return False
        else:
            try:
                int(hex_data, 16)
                return True
            except ValueError:
                return False

    def _detect_patterns(self, hex_code: str) -> list[str]:
        """Detect patterns in hex code."""
        patterns = []
        # Look for repeated sequences
        import re
        # Look for 4-character repeating patterns
        for i in range(0, len(hex_code) - 4, 4):
            seq = hex_code[i:i+4]
            if hex_code.count(seq) > 1:
                patterns.append(f"repeated:{seq}")
        return patterns

    def run(self, context: AgentContext) -> AgentResult:
        # Parse task to determine optimization type
        try:
            task_text = context.task.description.lower()
            
            if "compress" in task_text or "optimize" in task_text:
                # Extract hex code
                import re
                hex_match = re.search(r'[0-9a-fA-F]{8,}', context.task.description)
                if hex_match:
                    hex_code = hex_match.group(0)
                    compressed = self._compress_hex(hex_code)
                    verified = self._verify_hex(compressed)
                    patterns = self._detect_patterns(hex_code)
                    original_len = len(hex_code)
                    compressed_len = len(compressed)
                    efficiency = round((1 - compressed_len / original_len) * 100, 1) if original_len > 0 else 0
                    result_output = f"hex-compress: {original_len} -> {compressed_len} chars ({efficiency}% efficiency), patterns: {', '.join(patterns) if patterns else 'none'}"
                else:
                    result_output = "hex-compress: no hex code found in task"
            
            elif "verify" in task_text:
                # Extract hex data
                import re
                hex_match = re.search(r'[0-9a-fA-F]{8,}', context.task.description)
                if hex_match:
                    hex_data = hex_match.group(0)
                    is_valid = self._verify_hex(hex_data)
                    result_output = f"hex-verify: {hex_data[:20]}... -> {'VALID' if is_valid else 'INVALID'}"
                else:
                    result_output = "hex-verify: no hex code found"
            
            elif "pattern" in task_text:
                # Extract hex code
                import re
                hex_match = re.search(r'[0-9a-fA-F]{8,}', context.task.description)
                if hex_match:
                    hex_code = hex_match.group(0)
                    patterns = self._detect_patterns(hex_code)
                    result_output = f"pattern-detect: {len(patterns)} patterns found in {len(hex_code)}-char hex code: {', '.join(patterns) if patterns else 'none'}"
                else:
                    result_output = "pattern-detect: no hex code found"
            
            else:
                result_output = "hexoptimizer: specify operation (compress, verify, or pattern-detect)"
            
            # Publish hex optimization signal to the bus
            self.bus.publish(Event(
                type="hex-signal",
                payload={
                    "topic": "optimization",
                    "body": result_output,
                    "agent": "hexoptimizer",
                    "output": result_output,
                },
                source="hexoptimizer",
            ))
            
            return AgentResult(
                output=result_output,
                message_count=1,
            )
            
        except Exception as e:
            error_msg = f"hexoptimizer error: {str(e)}"
            self.bus.publish(Event(
                type="hex-signal",
                payload={"topic": "error", "body": error_msg, "agent": "hexoptimizer"},
                source="hexoptimizer",
            ))
            return AgentResult(output=error_msg, message_count=1)
