"""
Main program entry point for the AI Story Creator Pipeline.

Supports two modes of service communication:
- Local mode (default): call Python functions directly in-process
- RPC mode: call services A/B/C-hub/D over JSON-over-TCP (for Docker Compose)
"""
import sys
import json
import time
import os
from typing import Callable
from core.message import PipelineMessage
from core.pipeline import Pipeline
from core.timestamp_tracker import TimestampTracker
from core import rpc as _rpc


def main():
    """Main entry point for the pipeline program."""
    print("="*70)
    print(" " * 10 + "AI Story Creator & Multi-Media Enhancement Pipeline")
    print("="*70)
    print("\n📋 PROGRAM OVERVIEW:")
    print("   This program demonstrates a hybrid pipeline-parallel architecture:")
    print("   • Sequential pipeline: Story Generator → Analyzer → Aggregator")
    print("   • Parallel processing: Image, Audio, Translation, Formatting (simultaneous)")
    print("   • Complete timestamp tracking for performance measurement")
    # Determine execution mode
    rpc_mode = (os.environ.get("RPC_MODE", "false").lower() == "true") or (
        os.environ.get("PIPELINE_MODE", "").lower() == "rpc"
    )
    grpc_mode = os.environ.get("PIPELINE_MODE", "").lower() == "grpc"
    mode_label = "gRPC (Docker/remote services)" if grpc_mode else ("RPC (Docker/remote services)" if rpc_mode else "LOCAL (Baseline)")
    print("\n🔧 EXECUTION MODE:", mode_label)
    print("="*70)
    print("\n💡 INSTRUCTIONS:")
    print("   You can provide a story prompt in two ways:")
    print("   1. Command line: python main.py \"Your story prompt here\"")
    print("   2. Interactive: Just run python main.py and enter when prompted")
    print("\n📝 EXAMPLE PROMPTS:")
    print("   • \"A space adventure about robots\"")
    print("   • \"A fantasy tale with dragons and wizards\"")
    print("   • \"A modern detective story\"")
    print("   • \"An underwater exploration\"")
    print("="*70 + "\n")
    
    # Get user input
    if len(sys.argv) > 1:
        user_prompt = " ".join(sys.argv[1:])
        print(f"✅ Story prompt received from command line")
        print(f"   Prompt: '{user_prompt}'")
    else:
        print("📥 Please enter your story prompt:")
        print("   (You can describe a theme, scenario, or story idea)")
        user_prompt = input("   > ").strip()
        if not user_prompt:
            user_prompt = "A space adventure about robots"  # Default
            print(f"\n   ⚠️  No prompt provided. Using default: '{user_prompt}'")
        else:
            print(f"\n   ✅ Prompt received: '{user_prompt}'")
    
    print("\n" + "="*70)
    print("🚀 Starting pipeline execution...")
    print("="*70 + "\n")
    
    # Create initial message
    pipeline_start = time.time()
    message = PipelineMessage(user_input=user_prompt)
    
    # Create pipeline
    pipeline = Pipeline()
    
    # Helper: resolve host:port from env with sensible defaults
    def _addr_for(prefix: str, default_host: str, default_port: int) -> str:
        # Allow SERVICE_X_ADDR to override everything
        addr = os.environ.get(f"{prefix}_ADDR")
        if addr:
            return addr
        host = os.environ.get(f"{prefix}_HOST") or default_host
        port = (
            os.environ.get(f"{prefix}_PORT")
            or os.environ.get("SERVICE_PORT")
            or str(default_port)
        )
        return f"{host}:{port}"

    # Helper: merge results from src into dst PipelineMessage (preserve existing timestamps)
    def _merge_message(dst: PipelineMessage, src: PipelineMessage) -> PipelineMessage:
        if src.story_text is not None:
            dst.story_text = src.story_text
        if src.analysis is not None:
            dst.analysis = src.analysis
        if src.image_concept is not None:
            dst.image_concept = src.image_concept
        if src.audio_script is not None:
            dst.audio_script = src.audio_script
        if src.translations is not None:
            dst.translations = src.translations
        if src.formatted_output is not None:
            dst.formatted_output = src.formatted_output
        # Merge metadata (shallow)
        if src.metadata:
            dst.metadata.update(src.metadata)
        # Merge timestamps without clobbering existing
        for name, ts in src.timestamps.items():
            if name not in dst.timestamps:
                dst.timestamps[name] = ts
        return dst

    # Helper: build a service function that calls a remote RPC endpoint
    def _rpc_service(name: str, addr: str) -> Callable[[PipelineMessage], PipelineMessage]:
        host, _, port_s = addr.partition(":")
        port = int(port_s or "8000")

        def _call(msg: PipelineMessage) -> PipelineMessage:
            # Call remote and merge results into existing message to preserve local tracker marks
            resp = _rpc.rpc_call(host, port, msg.to_dict())
            remote = PipelineMessage.from_dict(resp)
            return _merge_message(msg, remote)

        _call.__name__ = f"rpc_{name}"
        return _call

    # Helper: build a service function that calls a remote gRPC endpoint
    def _grpc_service(name: str, addr: str) -> Callable[[PipelineMessage], PipelineMessage]:
        from core.grpc_client import PipelineClient

        host, _, port_s = addr.partition(":")
        port = int(port_s or "50051")
        client = PipelineClient(host, port)

        def _call(msg: PipelineMessage) -> PipelineMessage:
            # Call remote and merge results into existing message to preserve local tracker marks
            remote = client.process(msg)
            return _merge_message(msg, remote)

        _call.__name__ = f"grpc_{name}"
        return _call

    if grpc_mode or rpc_mode:
        # Resolve service addresses based on docker-compose defaults or env
        addr_a = _addr_for("SERVICE_A", "service-a", 50051)
        addr_b = _addr_for("SERVICE_B", "service-b", 50052)
        addr_c = _addr_for("SERVICE_C", "service-c", 50057)
        addr_d = _addr_for("SERVICE_D", "service-d", 50058)
        if grpc_mode:
            pipeline.register_service("service_a_story_generator", _grpc_service("service_a", addr_a))
            pipeline.register_service("service_b_story_analyzer", _grpc_service("service_b", addr_b))
            pipeline.register_service("service_c_parallel_hub", _grpc_service("service_c", addr_c))
            pipeline.register_service("service_d_aggregator", _grpc_service("service_d", addr_d))
        else:
            pipeline.register_service("service_a_story_generator", _rpc_service("service_a", addr_a))
            pipeline.register_service("service_b_story_analyzer", _rpc_service("service_b", addr_b))
            pipeline.register_service("service_c_parallel_hub", _rpc_service("service_c", addr_c))
            pipeline.register_service("service_d_aggregator", _rpc_service("service_d", addr_d))
    else:
        from services.service_a_story_generator import service_a
        from services.service_b_story_analyzer import service_b
        from services.service_c_parallel_hub import service_c
        from services.service_d_aggregator import service_d

        # Local in-process services
        pipeline.register_service("service_a_story_generator", service_a)
        pipeline.register_service("service_b_story_analyzer", service_b)
        pipeline.register_service("service_c_parallel_hub", service_c)
        pipeline.register_service("service_d_aggregator", service_d)
    
    # Define service chain
    service_chain = [
        "service_a_story_generator",
        "service_b_story_analyzer",
        "service_c_parallel_hub",
        "service_d_aggregator"
    ]
    
    try:
        # Execute pipeline
        tracker = TimestampTracker()
        tracker.mark_started(message, "main_program")
        
        final_message = pipeline.execute_pipeline(message, service_chain)
        
        tracker.mark_completed(final_message, "main_program")
        
        # Display execution timeline
        tracker.display_pipeline_execution(final_message)
        
        # Display results summary
        print("\n" + "="*60)
        print("Results Summary")
        print("="*60)
        
        if final_message.story_text:
            print(f"\n📖 Generated Story ({len(final_message.story_text.split())} words):")
            print("-" * 60)
            # Show first 300 characters
            story_preview = final_message.story_text[:300]
            if len(final_message.story_text) > 300:
                story_preview += "..."
            print(story_preview)
        
        if final_message.analysis:
            print(f"\n📊 Analysis:")
            print(f"  - Sentiment: {final_message.analysis.get('sentiment', 'N/A')}")
            print(f"  - Keywords: {', '.join(final_message.analysis.get('keywords', [])[:5])}")
            if final_message.analysis.get('characters'):
                print(f"  - Characters: {', '.join(final_message.analysis.get('characters', []))}")
        
        if final_message.image_concept:
            print(f"\n🎨 Image Concept:")
            print(f"  - Scene: {final_message.image_concept.get('scene_description', 'N/A')}")
            print(f"  - Mood: {final_message.image_concept.get('mood', 'N/A')}")
            print(f"  - Colors: {', '.join(final_message.image_concept.get('color_palette', []))}")
        
        if final_message.audio_script:
            print(f"\n🎙️ Audio Script:")
            print(f"  - Estimated Duration: {final_message.audio_script.get('duration_estimate_minutes', 0)} minutes")
            print(f"  - Tone: {final_message.audio_script.get('tone', 'N/A')}")
        
        if final_message.translations:
            print(f"\n🌐 Translations Available:")
            for lang in final_message.translations.keys():
                print(f"  - {lang.capitalize()}")
        
        if final_message.formatted_output:
            print(f"\n📄 Formatted Outputs Available:")
            for fmt in final_message.formatted_output.keys():
                print(f"  - {fmt.upper()}")
        
        # Optionally save full output to JSON (resolve path relative to this file)
        base_dir = os.path.dirname(__file__)
        if grpc_mode:
            output_file = os.path.join(base_dir, "output", "pipeline_output_grpc.json")
        elif rpc_mode:
            output_file = os.path.join(base_dir, "output", "pipeline_output_rpc.json")
        else:
            output_file = os.path.join(base_dir, "output", "pipeline_output_local.json")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        # Include execution mode in the saved JSON output
        output_payload = final_message.to_dict()
        output_payload["execution_mode"] = "grpc" if grpc_mode else ("rpc" if rpc_mode else "local")
        # Also mirror into metadata for consumers that only read metadata
        final_message.metadata["execution_mode"] = output_payload["execution_mode"]
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_payload, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Full output saved to: {output_file}")
        
        print("\n" + "="*60)
        print("Pipeline execution completed successfully!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during pipeline execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

