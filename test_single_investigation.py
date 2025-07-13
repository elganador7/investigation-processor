#!/usr/bin/env python3
"""
Test script to process a single investigation for testing purposes.
This allows you to verify the API connection and output format before running the full analysis.
"""

import json
import os
from investigation_processor import InvestigationProcessor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_single_investigation():
    """Test the processor with a single investigation."""
    
    # Check if API key is set
    if not os.getenv('PERPLEXITY_API_KEY'):
        print("Error: PERPLEXITY_API_KEY environment variable is required")
        print("Please set up your .env file with your Perplexity API key")
        return
    
    try:
        # Initialize processor
        processor = InvestigationProcessor()
        
        # Test with the first investigation
        test_investigation = processor.investigations[0]
        
        print(f"Testing with investigation: {test_investigation['title']}")
        print(f"Description: {test_investigation['description']}")
        print("\n" + "="*80)
        
        # Process the single investigation
        result = processor.process_investigation(test_investigation, 0)
        
        # Display results
        if result['success']:
            print("\n✅ SUCCESS: Analysis completed successfully!")
            print(f"Investigation: {result['investigation']}")
            print(f"Timestamp: {result['timestamp']}")
            print("\n" + "="*80)
            print("ANALYSIS RESULTS:")
            print("="*80)
            
            # Display each section
            for section_name, section_data in result['analysis_sections'].items():
                print(f"\n📊 {section_name.replace('_', ' ').upper()}:")
                print("-" * 40)
                if 'content' in section_data:
                    print(section_data['content'])
                else:
                    print(f"ERROR: {section_data['error']}")
                print()
            
            # Save test result
            with open('test_result.json', 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\n✅ Test result saved to test_result.json")
            
        else:
            print(f"\n❌ FAILED: {', '.join(result['errors'])}")
            print(f"Investigation: {result['investigation']}")
            print(f"Timestamp: {result['timestamp']}")
    
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        raise

if __name__ == "__main__":
    test_single_investigation() 