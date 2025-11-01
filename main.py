"""
Main program entry point for the AI Story Creator Pipeline.
Supports local execution mode (baseline for comparison).
"""
import sys
import json
import time
from core.message import PipelineMessage
from core.pipeline import Pipeline
from core.timestamp_tracker import TimestampTracker
from services.service_a_story_generator import service_a
from services.service_b_story_analyzer import service_b
from services.service_c_parallel_hub import service_c
from services.service_d_aggregator import service_d


def main():
    """Main entry point for the pipeline program."""
    print("="*60)
    print("AI Story Creator & Multi-Media Enhancement Pipeline")
    print("="*60)
    print("\nThis program demonstrates:")
    print("  - Sequential pipeline processing (A → B → D)")
    print("  - Parallel service execution (C1, C2, C3, C4)")
    print("  - Timestamp tracking through the entire pipeline")
    print("\nExecution Mode: LOCAL (Baseline)")
    print("="*60 + "\n")
    
    # Get user input
    if len(sys.argv) > 1:
        user_prompt = " ".join(sys.argv[1:])
    else:
        user_prompt = input("Enter a story prompt (e.g., 'A space adventure about robots'): ").strip()
        if not user_prompt:
            user_prompt = "A space adventure about robots"  # Default
            print(f"Using default prompt: {user_prompt}")
    
    print(f"\nProcessing prompt: '{user_prompt}'\n")
    
    # Create initial message
    pipeline_start = time.time()
    message = PipelineMessage(user_input=user_prompt)
    
    # Create pipeline
    pipeline = Pipeline()
    
    # Register services
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
        
        # Optionally save full output to JSON
        output_file = "pipeline_output.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_message.to_dict(), f, indent=2, ensure_ascii=False)
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

