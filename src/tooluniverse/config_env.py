"""
ToolUniverse Environment Configuration Module

Provides secure credential management and environment integration
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict

@dataclass
class ToolCredential:
    """Represents a tool credential"""
    name: str
    env_var: str
    service: str
    category: str
    priority: str  # CRITICAL, REQUIRED, RECOMMENDED, OPTIONAL
    is_set: bool
    needs_registration: bool = False
    registration_url: Optional[str] = None

class ToolUniverseConfig:
    """Manages ToolUniverse environment configuration"""
    
    # Credential definitions
    CREDENTIAL_SPECS = {
        # LLM Providers
        'OPENAI_API_KEY': {
            'service': 'OpenAI',
            'category': 'LLM',
            'priority': 'CRITICAL',
            'registration': 'https://platform.openai.com/api-keys'
        },
        'ANTHROPIC_API_KEY': {
            'service': 'Anthropic',
            'category': 'LLM',
            'priority': 'CRITICAL',
            'registration': 'https://console.anthropic.com'
        },
        'HF_TOKEN': {
            'service': 'Hugging Face',
            'category': 'LLM/Embeddings',
            'priority': 'CRITICAL',
            'registration': 'https://huggingface.co/settings/tokens'
        },
        'GEMINI_API_KEY': {
            'service': 'Google Gemini',
            'category': 'LLM',
            'priority': 'RECOMMENDED',
            'registration': 'https://ai.google.dev/tutorials/setup'
        },
        'DEEPSEEK_API_KEY': {
            'service': 'DeepSeek',
            'category': 'LLM',
            'priority': 'RECOMMENDED',
            'registration': 'https://platform.deepseek.com'
        },
        'OPENROUTER_API_KEY': {
            'service': 'OpenRouter',
            'category': 'LLM',
            'priority': 'RECOMMENDED',
            'registration': 'https://openrouter.ai/keys'
        },
        'OLLAMA_API_KEY': {
            'service': 'Ollama',
            'category': 'Local LLM',
            'priority': 'OPTIONAL',
            'registration': 'https://ollama.ai'
        },
        
        # Search & Data APIs
        'TAVILY_API_KEY': {
            'service': 'Tavily',
            'category': 'Web Search',
            'priority': 'RECOMMENDED',
            'registration': 'https://tavily.com'
        },
        'JINA_API_KEY': {
            'service': 'Jina AI',
            'category': 'Web Reading',
            'priority': 'RECOMMENDED',
            'registration': 'https://jina.ai/embeddings'
        },
        'EXA_API_KEY': {
            'service': 'Exa',
            'category': 'AI Search',
            'priority': 'RECOMMENDED',
            'registration': 'https://exa.ai'
        },
        'BRAVE_API_KEY': {
            'service': 'Brave',
            'category': 'Search Engine',
            'priority': 'RECOMMENDED',
            'registration': 'https://brave.com/search/api'
        },
        'NCBI_API_KEY': {
            'service': 'NCBI',
            'category': 'Biomedical Data',
            'priority': 'CRITICAL',
            'registration': 'https://www.ncbi.nlm.nih.gov/account/'
        },
        'SEMANTIC_SCHOLAR_API_KEY': {
            'service': 'Semantic Scholar',
            'category': 'Academic Search',
            'priority': 'RECOMMENDED',
            'registration': 'https://www.semanticscholar.org/product/api'
        },
        'CORE_API_KEY': {
            'service': 'CORE',
            'category': 'Academic Data',
            'priority': 'RECOMMENDED',
            'registration': 'https://core.ac.uk/services/api'
        },
        'ZOTERO_API_KEY': {
            'service': 'Zotero',
            'category': 'Citation Management',
            'priority': 'OPTIONAL',
            'registration': 'https://www.zotero.org/settings/keys'
        },
        
        # Biomedical Databases
        'BRENDA_EMAIL': {
            'service': 'BRENDA',
            'category': 'Enzyme Database',
            'priority': 'REQUIRED',
            'registration': 'https://www.brenda-enzymes.org/register.php'
        },
        'BRENDA_PASSWORD': {
            'service': 'BRENDA',
            'category': 'Enzyme Database',
            'priority': 'REQUIRED',
            'registration': 'https://www.brenda-enzymes.org/register.php'
        },
        'OMIM_API_KEY': {
            'service': 'OMIM',
            'category': 'Genetic Database',
            'priority': 'REQUIRED',
            'registration': 'https://omim.org/api'
        },
        'BIOGRID_ACCESS_KEY': {
            'service': 'BioGRID',
            'category': 'Protein Interactions',
            'priority': 'REQUIRED',
            'registration': 'https://webservice.thebiogrid.org/'
        },
        'DISGENET_API_KEY': {
            'service': 'DisGeNET',
            'category': 'Gene-Disease',
            'priority': 'REQUIRED',
            'registration': 'https://www.disgenet.org/registration'
        },
        'CLUE_API_KEY': {
            'service': 'CLUE.io',
            'category': 'Drug Repurposing',
            'priority': 'REQUIRED',
            'registration': 'https://clue.io'
        },
        'ADDGENE_API_KEY': {
            'service': 'Addgene',
            'category': 'Plasmid Repository',
            'priority': 'REQUIRED',
            'registration': 'https://www.addgene.org/contact/'
        },
        'ONCOKB_API_TOKEN': {
            'service': 'OncoKB',
            'category': 'Cancer Variants',
            'priority': 'REQUIRED',
            'registration': 'https://www.oncokb.org/apiAccess'
        },
        'MCULE_API_KEY': {
            'service': 'MCule',
            'category': 'Compound Sourcing',
            'priority': 'REQUIRED',
            'registration': 'https://mcule.com/signup'
        },
        'PHARMVAR_API_KEY': {
            'service': 'PharmVar',
            'category': 'Pharmacogenomics',
            'priority': 'RECOMMENDED',
            'registration': 'https://www.pharmvar.org/'
        },
        
        # Government/Regulatory
        'FDA_API_KEY': {
            'service': 'OpenFDA',
            'category': 'Regulatory',
            'priority': 'RECOMMENDED',
            'registration': 'https://open.fda.gov/apis/authentication/'
        },
        'USPTO_API_KEY': {
            'service': 'USPTO',
            'category': 'Patents',
            'priority': 'RECOMMENDED',
            'registration': 'https://developer.uspto.gov/'
        },
        'ICD_CLIENT_ID': {
            'service': 'WHO ICD-11',
            'category': 'Disease Classification',
            'priority': 'RECOMMENDED',
            'registration': 'https://icd.who.int/icdapi'
        },
        
        # Specialty
        'NVIDIA_API_KEY': {
            'service': 'NVIDIA NIM',
            'category': 'GPU Inference',
            'priority': 'OPTIONAL',
            'registration': 'https://build.nvidia.com/'
        },
        'NOMIC_API_KEY': {
            'service': 'Nomic',
            'category': 'Vector Visualization',
            'priority': 'OPTIONAL',
            'registration': 'https://atlas.nomic.ai/'
        },
        'ALPHA_VANTAGE_API_KEY': {
            'service': 'Alpha Vantage',
            'category': 'Financial Data',
            'priority': 'OPTIONAL',
            'registration': 'https://www.alphavantage.co/api/'
        },
    }
    
    def __init__(self, repo_root: Optional[Path] = None):
        if repo_root is None:
            repo_root = Path.cwd()
        
        self.repo_root = Path(repo_root)
        self.config_dir = self.repo_root / '.tooluniverse'
    
    def get_credentials_status(self) -> Dict[str, ToolCredential]:
        """Get status of all defined credentials"""
        status = {}
        
        for env_var, spec in self.CREDENTIAL_SPECS.items():
            is_set = env_var in os.environ and bool(os.environ[env_var])
            
            cred = ToolCredential(
                name=spec.get('service', env_var),
                env_var=env_var,
                service=spec.get('service', env_var),
                category=spec.get('category', 'Unknown'),
                priority=spec.get('priority', 'OPTIONAL'),
                is_set=is_set,
                registration_url=spec.get('registration')
            )
            status[env_var] = cred
        
        return status
    
    def get_missing_critical(self) -> List[ToolCredential]:
        """Get list of missing CRITICAL credentials"""
        status = self.get_credentials_status()
        return [c for c in status.values() if c.priority == 'CRITICAL' and not c.is_set]
    
    def get_missing_required(self) -> List[ToolCredential]:
        """Get list of missing REQUIRED credentials"""
        status = self.get_credentials_status()
        return [c for c in status.values() if c.priority == 'REQUIRED' and not c.is_set]
    
    def get_coverage(self) -> Dict[str, float]:
        """Get credential coverage by priority"""
        status = self.get_credentials_status()
        
        coverage = {}
        for priority in ['CRITICAL', 'REQUIRED', 'RECOMMENDED', 'OPTIONAL']:
            creds = [c for c in status.values() if c.priority == priority]
            if creds:
                found = sum(1 for c in creds if c.is_set)
                coverage[priority] = (found / len(creds)) * 100
        
        return coverage
    
    def print_status(self):
        """Print credential status report"""
        status = self.get_credentials_status()
        coverage = self.get_coverage()
        
        print("\n" + "="*70)
        print("ToolUniverse Credential Status Report")
        print("="*70)
        
        # Coverage summary
        print("\n📊 Coverage by Priority:")
        for priority, percent in sorted(coverage.items()):
            print(f"  {priority:12} {percent:5.1f}%")
        
        # Detailed status
        for priority in ['CRITICAL', 'REQUIRED', 'RECOMMENDED', 'OPTIONAL']:
            creds = [c for c in status.values() if c.priority == priority]
            if not creds:
                continue
            
            print(f"\n{priority}:")
            for cred in sorted(creds, key=lambda x: x.name):
                status_icon = "✓" if cred.is_set else "✗"
                print(f"  {status_icon} {cred.env_var:25} {cred.service:20} {cred.category}")
                if not cred.is_set and cred.registration_url:
                    print(f"      📝 Register: {cred.registration_url}")
        
        print("\n" + "="*70)
    
    def export_config(self, format='json'):
        """Export configuration as JSON/YAML"""
        status = self.get_credentials_status()
        coverage = self.get_coverage()
        
        config = {
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'coverage': coverage,
            'credentials': {
                k: {
                    'service': v.service,
                    'category': v.category,
                    'priority': v.priority,
                    'is_set': v.is_set,
                    'registration': v.registration_url
                }
                for k, v in status.items()
            }
        }
        
        if format == 'json':
            return json.dumps(config, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")

if __name__ == '__main__':
    config = ToolUniverseConfig()
    config.print_status()
    
    print("\n\n📋 JSON Export:")
    print(config.export_config('json'))

