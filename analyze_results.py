#!/usr/bin/env python3
"""
Utility script to analyze and visualize investigation results.
This script helps extract key insights from the generated analysis files.
"""

import json
import pandas as pd
import re
from typing import Dict, List, Any
from datetime import datetime
import os

class ResultsAnalyzer:
    def __init__(self, results_file: str):
        """Initialize analyzer with results file."""
        with open(results_file, 'r') as f:
            self.results = json.load(f)
        
        self.successful_results = [r for r in self.results if r['success']]
        self.failed_results = [r for r in self.results if not r['success']]
    
    def extract_market_sizes(self) -> pd.DataFrame:
        """Extract market size information from successful analyses."""
        market_data = []
        
        for result in self.successful_results:
            content = result['content']
            investigation = result['investigation']
            
            # Look for market size patterns
            market_size_patterns = [
                r'\$[\d,]+\.?\d*\s*(?:billion|million|trillion)',
                r'[\d,]+\.?\d*\s*(?:billion|million|trillion)\s*(?:USD|dollars)',
                r'market\s+size.*?\$[\d,]+\.?\d*',
                r'total\s+market.*?\$[\d,]+\.?\d*'
            ]
            
            market_sizes = []
            for pattern in market_size_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                market_sizes.extend(matches)
            
            market_data.append({
                'investigation': investigation,
                'market_sizes_found': market_sizes,
                'content_length': len(content)
            })
        
        return pd.DataFrame(market_data)
    
    def extract_tariff_impacts(self) -> pd.DataFrame:
        """Extract tariff impact information."""
        tariff_data = []
        
        for result in self.successful_results:
            content = result['content']
            investigation = result['investigation']
            
            # Look for tariff impact mentions
            tariff_patterns = {
                '10%': r'10%|ten\s+percent',
                '25%': r'25%|twenty\s+five\s+percent',
                '50%': r'50%|fifty\s+percent'
            }
            
            tariff_mentions = {}
            for rate, pattern in tariff_patterns.items():
                matches = re.findall(pattern, content, re.IGNORECASE)
                tariff_mentions[rate] = len(matches)
            
            tariff_data.append({
                'investigation': investigation,
                **tariff_mentions
            })
        
        return pd.DataFrame(tariff_data)
    
    def extract_companies(self) -> pd.DataFrame:
        """Extract company mentions from analyses."""
        company_data = []
        
        # Common company patterns
        company_patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Inc|Corp|LLC|Ltd|Company|Co)',
            r'(?:company|firm|manufacturer)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:reported|announced|stated)'
        ]
        
        for result in self.successful_results:
            content = result['content']
            investigation = result['investigation']
            
            companies = set()
            for pattern in company_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                companies.update(matches)
            
            for company in companies:
                if len(company.split()) >= 2:  # Filter out single words
                    company_data.append({
                        'investigation': investigation,
                        'company': company.strip(),
                        'mention_count': content.lower().count(company.lower())
                    })
        
        return pd.DataFrame(company_data)
    
    def generate_summary_stats(self) -> Dict[str, Any]:
        """Generate summary statistics."""
        total_investigations = len(self.results)
        successful_count = len(self.successful_results)
        failed_count = len(self.failed_results)
        
        # Calculate average content length
        avg_content_length = 0
        if successful_count > 0:
            total_length = sum(len(r['content']) for r in self.successful_results)
            avg_content_length = total_length / successful_count
        
        # Extract common themes
        all_content = ' '.join([r['content'] for r in self.successful_results])
        common_words = self._extract_common_words(all_content)
        
        return {
            'total_investigations': total_investigations,
            'successful_analyses': successful_count,
            'failed_analyses': failed_count,
            'success_rate': (successful_count / total_investigations) * 100 if total_investigations > 0 else 0,
            'average_content_length': avg_content_length,
            'common_themes': common_words[:10]
        }
    
    def _extract_common_words(self, text: str) -> List[tuple]:
        """Extract most common words from text."""
        # Remove common stop words and punctuation
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        # Clean text
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text.split()
        
        # Filter out stop words and short words
        words = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Count frequencies
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # Sort by frequency
        return sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    
    def save_analysis_report(self, output_file: str = None):
        """Save comprehensive analysis report."""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"analysis_report_{timestamp}.json"
        
        # Generate all analyses
        market_sizes = self.extract_market_sizes()
        tariff_impacts = self.extract_tariff_impacts()
        companies = self.extract_companies()
        summary_stats = self.generate_summary_stats()
        
        # Compile report
        report = {
            'summary_statistics': summary_stats,
            'market_sizes': market_sizes.to_dict('records'),
            'tariff_impacts': tariff_impacts.to_dict('records'),
            'companies': companies.to_dict('records'),
            'failed_investigations': [
                {
                    'investigation': r['investigation'],
                    'error': r['error']
                } for r in self.failed_results
            ],
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        # Save report
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Analysis report saved to {output_file}")
        return report

def main():
    """Main function to run analysis."""
    # Look for the most recent results file
    results_files = [f for f in os.listdir('.') if f.startswith('investigation_results_') and f.endswith('.json')]
    
    if not results_files:
        print("No investigation results files found!")
        print("Please run the investigation processor first.")
        return
    
    # Use the most recent file
    latest_file = max(results_files)
    print(f"Analyzing results from: {latest_file}")
    
    try:
        analyzer = ResultsAnalyzer(latest_file)
        report = analyzer.save_analysis_report()
        
        # Print summary
        stats = report['summary_statistics']
        print(f"\n📊 ANALYSIS SUMMARY:")
        print(f"Total investigations: {stats['total_investigations']}")
        print(f"Successful analyses: {stats['successful_analyses']}")
        print(f"Failed analyses: {stats['failed_analyses']}")
        print(f"Success rate: {stats['success_rate']:.1f}%")
        print(f"Average content length: {stats['average_content_length']:.0f} characters")
        
        print(f"\n🔍 TOP THEMES:")
        for word, count in stats['common_themes'][:5]:
            print(f"  {word}: {count} mentions")
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        raise

if __name__ == "__main__":
    main() 