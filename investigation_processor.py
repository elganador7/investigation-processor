import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from prompts import get_all_prompts

# Load environment variables
load_dotenv()

class InvestigationProcessor:
    def __init__(self):
        self.perplexity_api_key = os.getenv('PERPLEXITY_API_KEY')
        if not self.perplexity_api_key:
            raise ValueError("PERPLEXITY_API_KEY environment variable is required")
        
        # Initialize OpenAI client with Perplexity API
        self.client = OpenAI(
            api_key=self.perplexity_api_key,
            base_url="https://api.perplexity.ai"
        )
        
        # Load investigations data
        with open('ongoing_investigations.json', 'r') as f:
            self.investigations = json.load(f)
    
    def create_market_assessment_prompts(self, investigation: Dict[str, str]) -> Dict[str, str]:
        """Create four separate prompts for different aspects of market assessment."""
        return get_all_prompts(investigation)
    
    def call_perplexity_api(self, prompt: str, investigation_title: str) -> Dict[str, Any]:
        """Make API call to Perplexity with error handling and retries."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="sonar-pro",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=4000,
                    temperature=0.1
                )
                
                if response.choices and len(response.choices) > 0:
                    return {
                        'success': True,
                        'content': response.choices[0].message.content,
                        'investigation': investigation_title,
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    raise Exception("No content in response")
                    
            except Exception as e:
                print(f"API call failed for {investigation_title} (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return {
                        'success': False,
                        'error': str(e),
                        'investigation': investigation_title,
                        'timestamp': datetime.now().isoformat()
                    }
        
        return {
            'success': False,
            'error': 'Max retries exceeded',
            'investigation': investigation_title,
            'timestamp': datetime.now().isoformat()
        }
    
    def process_investigation(self, investigation: Dict[str, str], index: int) -> Dict[str, Any]:
        """Process a single investigation with four separate API calls."""
        print(f"\nProcessing investigation {index + 1}/{len(self.investigations)}: {investigation['title']}")
        
        # Create the four separate prompts
        prompts = self.create_market_assessment_prompts(investigation)
        
        # Initialize result structure
        result = {
            'investigation': investigation['title'],
            'timestamp': datetime.now().isoformat(),
            'investigation_data': investigation,
            'analysis_sections': {},
            'success': True,
            'errors': []
        }
        
        # Process each section separately
        for section_name, prompt in prompts.items():
            print(f"  Processing {section_name.replace('_', ' ').title()}...")
            
            try:
                section_result = self.call_perplexity_api(prompt, f"{investigation['title']} - {section_name}")
                
                if section_result['success']:
                    result['analysis_sections'][section_name] = {
                        'content': section_result['content'],
                        'timestamp': section_result['timestamp']
                    }
                else:
                    result['analysis_sections'][section_name] = {
                        'error': section_result['error'],
                        'timestamp': section_result['timestamp']
                    }
                    result['errors'].append(f"{section_name}: {section_result['error']}")
                    
            except Exception as e:
                error_msg = f"Failed to process {section_name}: {str(e)}"
                result['analysis_sections'][section_name] = {
                    'error': error_msg,
                    'timestamp': datetime.now().isoformat()
                }
                result['errors'].append(error_msg)
            
            # Add delay between API calls for the same investigation
            if section_name != list(prompts.keys())[-1]:  # Not the last section
                time.sleep(2)
        
        # Mark as failed if any critical sections failed
        if len(result['errors']) > 0:
            result['success'] = False
        
        return result
    
    def process_all_investigations(self) -> List[Dict[str, Any]]:
        """Process all investigations and return results."""
        results = []
        
        print(f"Starting analysis of {len(self.investigations)} investigations...")
        
        for i, investigation in enumerate(self.investigations):
            result = self.process_investigation(investigation, i)
            results.append(result)
            
            # Save progress after each investigation
            self.save_results(results, f"investigation_results_progress_{i+1}.json")
            
            # Add delay between API calls to avoid rate limiting
            if i < len(self.investigations) - 1:
                print("Waiting 5 seconds before next API call...")
                time.sleep(5)
        
        return results
    
    def save_results(self, results: List[Dict[str, Any]], filename: str = None):
        """Save results to JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"investigation_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Results saved to {filename}")
    
    def generate_summary_report(self, results: List[Dict[str, Any]]) -> str:
        """Generate a summary report of all investigations."""
        successful_results = [r for r in results if r['success']]
        failed_results = [r for r in results if not r['success']]
        
        report = f"""
# Investigation Analysis Summary Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Overview
- Total investigations processed: {len(results)}
- Successful analyses: {len(successful_results)}
- Failed analyses: {len(failed_results)}

## Successful Analyses
"""
        
        for result in successful_results:
            report += f"\n### {result['investigation']}\n"
            report += f"**Source:** {result['investigation_data']['source']}\n\n"
            
            # Show summary of each section
            for section_name, section_data in result['analysis_sections'].items():
                if 'content' in section_data:
                    report += f"**{section_name.replace('_', ' ').title()}:**\n"
                    report += section_data['content'][:300] + "...\n\n"
                else:
                    report += f"**{section_name.replace('_', ' ').title()}:** Error - {section_data['error']}\n\n"
            
            report += "---\n"
        
        if failed_results:
            report += "\n## Failed Analyses\n"
            for result in failed_results:
                report += f"- {result['investigation']}: {', '.join(result['errors'])}\n"
        
        return report
    
    def save_summary_report(self, results: List[Dict[str, Any]]):
        """Save summary report to markdown file."""
        report = self.generate_summary_report(results)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"investigation_summary_report_{timestamp}.md"
        
        with open(filename, 'w') as f:
            f.write(report)
        
        print(f"Summary report saved to {filename}")

def main():
    """Main execution function."""
    try:
        # Initialize processor
        processor = InvestigationProcessor()
        
        # Process all investigations
        results = processor.process_all_investigations()
        
        # Save final results
        processor.save_results(results)
        
        # Generate and save summary report
        processor.save_summary_report(results)
        
        print("\nAnalysis complete! Check the generated files for results.")
        
    except Exception as e:
        print(f"Error during processing: {str(e)}")
        raise

if __name__ == "__main__":
    main() 