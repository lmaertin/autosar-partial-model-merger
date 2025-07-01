"""
Example usage of the ARXML Merger with real example files
"""

from pathlib import Path
from arxml_merger import ArxmlMerger, MergeConfig, ConflictResolutionStrategy

def main():
    print("ARXML Merger Example")
    print("===================")
    
    # Paths to the example files
    current_dir = Path(__file__).parent
    sample1_path = current_dir / "sample1.arxml"
    sample2_path = current_dir / "sample2.arxml"
    output_path = current_dir / "merged_example.arxml"
    
    # Check if example files exist
    if not sample1_path.exists():
        print(f"❌ Example file not found: {sample1_path}")
        print("   Make sure sample1.arxml is in the examples/ folder")
        return
    if not sample2_path.exists():
        print(f"❌ Example file not found: {sample2_path}")
        print("   Make sure sample2.arxml is in the examples/ folder")
        return
    
    print("📁 Input files:")
    print(f"   - {sample1_path.name} ({sample1_path.stat().st_size} bytes)")
    print(f"   - {sample2_path.name} ({sample2_path.stat().st_size} bytes)")
    print(f"📄 Output file: {output_path.name}")
    print()
    
    # Create configuration
    config = MergeConfig(
        conflict_resolution=ConflictResolutionStrategy.MERGE_ALL,
        validate_schema=True,
        preserve_comments=True,
        output_encoding="utf-8"
    )
    
    print("⚙️ Configuration:")
    print(f"   - Conflict resolution: {config.conflict_resolution.value}")
    print(f"   - Schema validation: {config.validate_schema}")
    print(f"   - Preserve comments: {config.preserve_comments}")
    print()
    
    try:
        # Create merger
        merger = ArxmlMerger(config)
        
        print("🔄 Starting merge process...")
        
        # Merge files
        result = merger.merge_files([sample1_path, sample2_path])
        
        print("✅ Merge successful!")
        print("📊 Statistics:")
        print(f"   - Files processed: {result.statistics.files_processed}")
        print(f"   - Elements merged: {result.statistics.elements_merged}")
        print(f"   - Conflicts detected: {result.statistics.conflicts_found}")
        
        if hasattr(result, 'conflicts') and result.conflicts:
            print("   - Conflicts:")
            for i, conflict in enumerate(result.conflicts[:3], 1):
                print(f"     {i}. {conflict}")
        print()
        
        # Save result
        print("💾 Saving result...")
        result.save(output_path)
        
        if output_path.exists():
            file_size = output_path.stat().st_size
            print(f"✅ File saved: {output_path.name} ({file_size} bytes)")
            
            # Brief analysis of the result
            print("\n📋 Result analysis:")
            root = result.merged_tree
            
            # Count different element types
            components = len([e for e in root.iter() if e.tag.endswith('APPLICATION-SW-COMPONENT-TYPE')])
            interfaces = len([e for e in root.iter() if e.tag.endswith('SENDER-RECEIVER-INTERFACE')])
            packages = len([e for e in root.iter() if e.tag.endswith('AR-PACKAGE')])
            systems = len([e for e in root.iter() if e.tag.endswith('SYSTEM')])
            
            print(f"   - SW Components: {components}")
            print(f"   - Interfaces: {interfaces}")
            print(f"   - AR-Packages: {packages}")
            print(f"   - Systems: {systems}")
            
        else:
            print("❌ Error saving file!")
            
    except Exception as e:
        print(f"❌ Merge error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n🎉 Example completed successfully!")
    print("\n💡 Tips:")
    print("   - Open merged_example.arxml to see the result")
    print("   - Use the CLI for more options:")
    print("     python -m arxml_merger.cli -i sample1.arxml sample2.arxml -o output.arxml")
    print("   - Debug with VS Code: Select 'Python: Run Example Usage' in launch configurations")

def demo_conflict_strategies():
    """Demonstrates different conflict resolution strategies"""
    print("\n" + "="*60)
    print("Conflict Resolution Strategies Demo")
    print("="*60)
    
    current_dir = Path(__file__).parent
    sample1_path = current_dir / "sample1.arxml"
    sample2_path = current_dir / "sample2.arxml"
    
    if not (sample1_path.exists() and sample2_path.exists()):
        print("❌ Example files not found!")
        return
    
    strategies = [
        ("MERGE_ALL", ConflictResolutionStrategy.MERGE_ALL, "Merge all elements together"),
        ("FIRST_WINS", ConflictResolutionStrategy.FIRST_WINS, "First file wins on conflicts"),
        ("LAST_WINS", ConflictResolutionStrategy.LAST_WINS, "Last file wins on conflicts"),
    ]
    
    for name, strategy, description in strategies:
        print(f"\n🔧 Strategy: {name}")
        print(f"   📖 {description}")
        
        config = MergeConfig(conflict_resolution=strategy)
        merger = ArxmlMerger(config)
        
        try:
            result = merger.merge_files([sample1_path, sample2_path])
            output_file = current_dir / f"merged_{name.lower()}.arxml"
            result.save(output_file)
            
            print(f"   ✅ Success - {result.statistics.elements_merged} elements")
            print(f"   📄 Saved as: {output_file.name}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    main()
    demo_conflict_strategies()
