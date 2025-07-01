"""
Command Line Interface for the ARXML Merger
"""

import argparse
import sys
from pathlib import Path
from typing import List

from arxml_merger import ArxmlMerger, MergeConfig, ConflictResolutionStrategy
from arxml_merger.core.exceptions import ArxmlMergerException, InvalidArxmlFileError


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="AUTOSAR ARXML Merger - Merges partial ARXML models based on Splitable Elements",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i model1.arxml model2.arxml -o merged.arxml
  %(prog)s -i *.arxml -o result.arxml --conflict-resolution last_wins
  %(prog)s -i model1.arxml model2.arxml -o merged.arxml --validate-schema
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        nargs='+',
        required=True,
        help='Input ARXML files to merge'
    )
    
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Output file for merge result'
    )
    
    parser.add_argument(
        '--conflict-resolution',
        choices=['merge_all', 'first_wins', 'last_wins', 'fail'],
        default='merge_all',
        help='Conflict resolution strategy (default: merge_all)'
    )
    
    parser.add_argument(
        '--validate-schema',
        action='store_true',
        help='Validate against AUTOSAR schema'
    )
    
    parser.add_argument(
        '--preserve-comments',
        action='store_true',
        default=True,
        help='Preserve XML comments (default: True)'
    )
    
    parser.add_argument(
        '--encoding',
        default='utf-8',
        help='Output encoding (default: utf-8)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Log level (default: INFO)'
    )
    
    parser.add_argument(
        '--verbose-merge',
        action='store_true',
        help='Enable verbose merge output showing detailed element paths'
    )
    
    parser.add_argument(
        '--log-file',
        help='Log file (optional)'
    )
    
    parser.add_argument(
        '--pretty-print',
        action='store_true',
        default=True,
        help='Pretty print XML output (default: True)'
    )
    
    return parser.parse_args()


def create_merge_config(args: argparse.Namespace) -> MergeConfig:
    """Creates MergeConfig from Command Line Arguments"""
    conflict_resolution_map = {
        'merge_all': ConflictResolutionStrategy.MERGE_ALL,
        'first_wins': ConflictResolutionStrategy.FIRST_WINS,
        'last_wins': ConflictResolutionStrategy.LAST_WINS,
        'fail': ConflictResolutionStrategy.FAIL_ON_CONFLICT
    }
    
    return MergeConfig(
        conflict_resolution=conflict_resolution_map[args.conflict_resolution],
        validate_schema=args.validate_schema,
        preserve_comments=args.preserve_comments,
        output_encoding=args.encoding,
        verbose_merge=args.verbose_merge
    )


def validate_input_files(file_paths: List[str]) -> List[Path]:
    """Validates input files"""
    validated_paths = []
    
    for file_path in file_paths:
        path = Path(file_path)
        if not path.exists():
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            sys.exit(1)
        
        if not path.suffix.lower() in ['.arxml', '.xml']:
            print(f"Warning: File has no .arxml/.xml extension: {file_path}", file=sys.stderr)
        
        validated_paths.append(path)
    
    return validated_paths


def main():
    """Main function for CLI"""
    try:
        args = parse_arguments()
        
        # Validate input files
        input_files = validate_input_files(args.input)
        
        # Create output directory if needed
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create merge configuration
        config = create_merge_config(args)
        
        # Setup Logging
        from arxml_merger.utils import setup_logging
        logger = setup_logging(
            log_level=args.log_level,
            log_file=Path(args.log_file) if args.log_file else None
        )
        
        logger.info("Starting ARXML merge with %d files", len(input_files))
        logger.info("Output: %s", output_path)
        logger.info("Conflict resolution: %s", args.conflict_resolution)
        
        # Create merger and perform merge
        merger = ArxmlMerger(config)
        result = merger.merge_files(input_files)
        
        # Save result
        result.save(output_path, pretty_print=args.pretty_print)
        
        # Show statistics
        stats = result.statistics
        print("✓ Merge completed successfully!")
        print(f"  Files processed: {stats.files_processed}")
        print(f"  Elements merged: {stats.elements_merged}")
        print(f"  Processing time: {stats.processing_time:.2f}s")
        print(f"  Schema version: {stats.schema_version}")
        
        if result.conflicts:
            print(f"  Conflicts found: {len(result.conflicts)}")
            print(f"  Conflicts resolved: {len([c for c in result.conflicts if c.resolved_value is not None])}")
            
            if result.has_conflicts():
                print("\n! Unresolved conflicts:")
                for conflict in result.get_unresolved_conflicts():
                    print(f"    - {conflict.element_path}: {conflict.conflicting_values}")
        
        print(f"\nResult saved to: {output_path}")
        
    except KeyboardInterrupt:
        print("\nMerge cancelled by user", file=sys.stderr)
        sys.exit(130)
    except (ArxmlMergerException, InvalidArxmlFileError) as e:
        print(f"Error during merge: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
