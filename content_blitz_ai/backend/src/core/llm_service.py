import time

from dataclasses import dataclass
from typing import Any, Dict, Generator
from src.core.llm_pricing import calculate_llm_cost

@dataclass
class LLMResponse:
    content: str
    metadata: Dict[str, Any]
    usage: Dict[str, Any]


class LLMService:

    @staticmethod
    def invoke(
        llm: Any,
        prompt: str,
        state=None,
        agent: str | None = None,
        operation: str | None = None,
    ) -> LLMResponse:

        start = time.time()

        try:
            response = llm.invoke(prompt)

            latency = round(time.time() - start, 3)

            metadata = getattr(
                response,
                "response_metadata",
                {}
            )
            usage = getattr(
            response,
            "usage_metadata",
            {})

            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)
            total_tokens = usage.get("total_tokens", 0)

            model = metadata.get(
            "model_name",
            getattr(llm, "model", "unknown")
            )

            cost = calculate_llm_cost(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            )

            if state is not None:
                state.setdefault("trace", []).append({
                "trace_id": state.get("trace_id"),
                "agent": agent,
                "action": "llm_call",
                "operation": operation,
                "timestamp": time.time(),
                "latency": latency,
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "cost": cost,

                "status": "success",
                "metadata": metadata,
                })

            return LLMResponse(
                content=str(
                    getattr(response, "content", "")
                ).strip(),
                metadata=metadata,
                usage=usage
            )

        except Exception as e:

            latency = round(time.time() - start, 3)

            if state is not None:
                state.setdefault("trace", []).append({
                    "trace_id": state.get("trace_id"),
                    "agent": agent,
                    "action": "llm_call",
                    "operation": operation,
                    "timestamp": time.time(),
                    "latency": latency,
                    "status": "failed",
                    "error": str(e),
                })

            raise

    @staticmethod
    def stream(
        llm: Any,
        prompt: str,
        state=None,
        agent: str | None = None,
        operation: str | None = None,
    ) -> Generator[str, None, LLMResponse]:
    
        start = time.time()
        first_token_time = None
        full_response = ""
        metadata = {}
        accumulated_message = None
    
        try:
        
            for chunk in llm.stream(prompt):
            
                # Accumulate the complete AIMessage
                if accumulated_message is None:
                    accumulated_message = chunk
                else:
                    accumulated_message += chunk
    
                text = getattr(chunk, "content", "")
    
                if not text:
                    continue
                
                if first_token_time is None:
                    first_token_time = time.time()
    
                full_response += text
    
                yield text
    
            # Get metadata/usage from accumulated message
            metadata = getattr(
                accumulated_message,
                "response_metadata",
                {}
            )
    
            usage = getattr(
                accumulated_message,
                "usage_metadata",
                {}
            )
    
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)
            total_tokens = usage.get("total_tokens", 0)
    
            model = metadata.get(
                "model_name",
                getattr(llm, "model", "unknown")
            )
    
            cost = calculate_llm_cost(
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )
    
            latency = round(
                time.time() - start,
                3
            )
    
            time_to_first_token = (
                round(
                    first_token_time - start,
                    3
                )
                if first_token_time is not None
                else None
            )
    
            if state is not None:
            
                state.setdefault("trace", []).append({
                    "trace_id": state.get("trace_id"),
                    "agent": agent,
                    "action": "llm_stream",
                    "operation": operation,
                    "timestamp": time.time(),
                    "latency": latency,
                    "time_to_first_token": time_to_first_token,
                    "output_length": len(full_response),
    
                    "model": model,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens,
                    "cost": cost,
    
                    "status": "success",
                    "metadata": metadata,
                })
    
            return LLMResponse(
                content=full_response.strip(),
                metadata=metadata,
                usage=usage
            )
    
        except Exception as e:
        
            latency = round(
                time.time() - start,
                3
            )
    
            if state is not None:
            
                state.setdefault("trace", []).append({
                    "trace_id": state.get("trace_id"),
                    "agent": agent,
                    "action": "llm_stream",
                    "operation": operation,
                    "timestamp": time.time(),
                    "latency": latency,
                    "status": "failed",
                    "error": str(e),
                })
    
            raise