from __future__ import annotations

from .base import AgentContext, AgentResult, BaseAgent
from ..bus import Event


class HexConverter(BaseAgent):
    """Agent specialized in code-to-hex conversion and vice versa.
    
    This agent converts Python and other code formats into hexadecimal strings
    for memory storage and transmission, and can reverse the process. It serves
    as the organism's "translator" between human-readable code and hex representation.
    """
    
    name = "hexconverter"
    role = "code-to-hex conversion specialist"
    capabilities = [
        "code-to-hex",
        "hex-to-code", 
        "syntax-validate",
        "memory-index",
    ]
    tool_names = []

    def __init__(self, llm, registry, memory, bus, run_id: str) -> None:
        super().__init__(llm, registry, memory, bus, run_id)

    def system_prompt(self) -> str:
        return (
            "You are the HEXCONVERTER of IXPANSION — the organism's code translator. "
            "You convert Python and programming code into hexadecimal strings for "
            "memory storage and transmission, and can reverse the process. You are "
            "not a compiler; you are a translator. Every conversion must be exact and "
            "reversible. Report conversion results with precise hex output and "
            "reversibility confirmation."
        )

    def _code_to_hex(self, code: str) -> str:
        """Convert Python code to hex representation."""
        import base64
        try:
            # Use base64 as the conversion method
            hex_result = base64.b64encode(code.encode()).hex()
            return hex_result
        except Exception as e:
            return f"ERROR: {str(e)}"

    def _hex_to_code(self, hex_str: str) -> str:
        """Convert hex back to Python code."""
        import base64
        try:
            # Reverse the base64 hex conversion
            # Add padding if needed
            hex_str = hex_str.strip()
            if len(hex_str) % 2 != 0:
                hex_str = hex_str + "0"  # Fix odd-length hex
            byte_data = bytes.fromhex(hex_str)
            code_result = base64.b64decode(byte_data).decode()
            return code_result
        except Exception as e:
            return f"ERROR: {str(e)}"

    def _validate_hex(self, hex_str: str) -> bool:
        """Validate that a string is valid hexadecimal."""
        try:
            int(hex_str, 16)
            return True
        except ValueError:
            return False

    def run(self, context: AgentContext) -> AgentResult:
        # Parse the task to determine conversion type
        try:
            task_text = context.task.description.lower()
            
            if "hex-to-code" in task_text or "reverse" in task_text:
                # Extract hex string from task
                import re
                hex_match = re.search(r'[0-9a-fA-F]{8,}', context.task.description)
                if hex_match:
                    hex_str = hex_match.group(0)
                    code = self._hex_to_code(hex_str)
                    result_output = f"hex-to-code: {hex_str} -> {code[:100]}..."
                else:
                    result_output = "hex-to-code: no hex string found in task"
            
            elif "code-to-hex" in task_text or "convert" in task_text:
                # Extract code from task
                # Get the code - typically after "convert" or "this code"
                code_lines = context.task.description.split("\n")
                code = ""
                for line in code_lines:
                    if not line.startswith("#") and line.strip():
                        code = line
                        break
                if code:
                    hex_result = self._code_to_hex(code)
                    result_output = f"code-to-hex: {code[:50]}... -> {hex_result[:50]}..."
                else:
                    result_output = "code-to-hex: no code found in task"
            
            elif "validate" in task_text:
                # Extract hex string to validate
                import re
                hex_match = re.search(r'[0-9a-fA-F]{8,}', context.task.description)
                if hex_match:
                    hex_str = hex_match.group(0)
                    is_valid = self._validate_hex(hex_str)
                    result_output = f"validate-hex: {hex_str} -> {'VALID' if is_valid else 'INVALID'}"
                else:
                    result_output = "validate-hex: no hex string found"
            
            else:
                result_output = "hexconverter: specify conversion type (code-to-hex, hex-to-code, or validate)"

            # Publish hex conversion signal to the bus
            self.bus.publish(Event(
                type="hex-signal",
                payload={
                    "topic": "conversion",
                    "body": result_output,
                    "agent": "hexconverter",
                    "output": result_output,
                },
                source="hexconverter",
            ))
            
            return AgentResult(
                output=result_output,
                message_count=1,
            )
            
        except Exception as e:
            error_msg = f"hexconverter error: {str(e)}"
            self.bus.publish(Event(
                type="hex-signal",
                payload={"topic": "error", "body": error_msg, "agent": "hexconverter"},
                source="hexconverter",
            ))
            return AgentResult(output=error_msg, message_count=1)
