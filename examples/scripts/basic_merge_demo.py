"""
Basic ARXML Merge Demo
This script demonstrates how to merge AUTOSAR ARXML files using the arxml_merger library.
It uses the basic engine control examples to show different merge strategies.
"""

from pathlib import Path
import sys
import os

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from arxml_merger import ArxmlMerger, MergeConfig, ConflictResolutionStrategy

def main():
    print("ARXML Merger - Basic Demo")
    print("========================")
    
    # Paths to the example files
    current_dir = Path(__file__).parent.parent
    base_model = current_dir / "basic_merge" / "engine_control_base.arxml"
    extended_model = current_dir / "basic_merge" / "engine_control_extended.arxml"
    output_dir = current_dir / "generated"
    
    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)
    
    # Check if example files exist
    if not base_model.exists():
        print(f"❌ Example file not found: {base_model}")
        print("   Make sure engine_control_base.arxml is in the basic_merge/ folder")
        return
    if not extended_model.exists():
        print(f"❌ Example file not found: {extended_model}")
        print("   Make sure engine_control_extended.arxml is in the basic_merge/ folder")
        return
    
    print("📁 Input files:")
    print(f"   - {base_model.name} ({base_model.stat().st_size} bytes)")
    print(f"   - {extended_model.name} ({extended_model.stat().st_size} bytes)")
    
    # Demonstrate different merge strategies
    strategies = [
        (ConflictResolutionStrategy.MERGE_ALL, "merge_all"),
        (ConflictResolutionStrategy.FIRST_WINS, "first_wins"), 
        (ConflictResolutionStrategy.LAST_WINS, "last_wins")
    ]
    
    for strategy, strategy_name in strategies:
        print(f"\n🔄 Testing merge strategy: {strategy_name}")
        output_path = output_dir / f"engine_control_{strategy_name}.arxml"
        
        try:
            # Create merge configuration
            config = MergeConfig(
                conflict_resolution=strategy,
                preserve_comments=True,
                preserve_formatting=True,
                verbose_merge=False  # Set to False for cleaner output
            )
            
            # Create merger instance
            merger = ArxmlMerger(config)
            
            # Perform merge
            print(f"   Merging {base_model.name} + {extended_model.name}")
            result = merger.merge_files([base_model, extended_model])
            
            # Save result
            result.save(output_path)
            
            if output_path.exists():
                file_size = output_path.stat().st_size
                print(f"   ✅ Saved: {output_path.name} ({file_size} bytes)")
                
                # Show merge statistics
                try:
                    stats = result.get_merge_statistics()
                    print(f"   📊 Elements merged: {stats.get('elements_merged', 0)}")
                    print(f"   ⚠️  Conflicts found: {stats.get('conflicts_found', 0)}")
                except AttributeError:
                    # If get_merge_statistics doesn't exist, skip it
                    print("   📊 Merge completed successfully")
            else:
                print(f"   ❌ Failed to save {output_path.name}")
                
        except Exception as e:
            print(f"   ❌ Error during {strategy_name} merge: {e}")
    
    print("\n🎉 Demo completed!")
    print(f"   Check the generated files in: {output_dir}")

def demonstrate_conflict_scenarios():
    """Demonstrate conflict resolution with the sensor model examples."""
    print("\nConflict Resolution Demo")
    print("=======================")
    
    current_dir = Path(__file__).parent.parent
    sensor_v1 = current_dir / "conflict_scenarios" / "sensor_model_v1.arxml"
    sensor_v2 = current_dir / "conflict_scenarios" / "sensor_model_v2.arxml"
    output_dir = current_dir / "generated"
    
    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)
    
    if not sensor_v1.exists() or not sensor_v2.exists():
        print("❌ Sensor model files not found - skipping conflict demo")
        return
    
    print("📁 Conflict scenario files:")
    print(f"   - {sensor_v1.name} ({sensor_v1.stat().st_size} bytes)")
    print(f"   - {sensor_v2.name} ({sensor_v2.stat().st_size} bytes)")
    
    # Test conflict resolution strategies
    strategies = [
        (ConflictResolutionStrategy.MERGE_ALL, "merge_all"),
        (ConflictResolutionStrategy.FIRST_WINS, "first_wins"),
        (ConflictResolutionStrategy.LAST_WINS, "last_wins")
    ]
    
    for strategy, strategy_name in strategies:
        print(f"\n🔄 Conflict resolution: {strategy_name}")
        output_path = output_dir / f"sensor_conflict_{strategy_name}.arxml"
        
        try:
            config = MergeConfig(
                conflict_resolution=strategy,
                preserve_comments=True,
                preserve_formatting=True,
                verbose_merge=False
            )
            
            merger = ArxmlMerger(config)
            result = merger.merge_files([sensor_v1, sensor_v2])
            result.save(output_path)
            
            if output_path.exists():
                file_size = output_path.stat().st_size
                print(f"   ✅ Saved: {output_path.name} ({file_size} bytes)")
                
                try:
                    stats = result.get_merge_statistics()
                    print(f"   📊 Elements merged: {stats.get('elements_merged', 0)}")
                    print(f"   ⚠️  Conflicts found: {stats.get('conflicts_found', 0)}")
                except AttributeError:
                    print("   📊 Merge completed successfully")
                
        except Exception as e:
            print(f"   ❌ Error during conflict resolution: {e}")

if __name__ == "__main__":
    main()
    demonstrate_conflict_scenarios()
