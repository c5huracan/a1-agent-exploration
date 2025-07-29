#!/usr/bin/env python3
"""
Test DSPy setup and basic functionality
"""
import os
import dspy

def test_dspy_setup():
    """Verify DSPy installation and basic functionality"""
    print("🔬 DSPy Setup Test")
    print("=" * 30)
    
    try:
        # Test basic DSPy import
        print(f"✅ DSPy version: {dspy.__version__ if hasattr(dspy, '__version__') else 'installed'}")
        
        # Test basic signature creation
        class SimpleSignature(dspy.Signature):
            """Test signature for verification"""
            input_text = dspy.InputField()
            output_text = dspy.OutputField()
        
        print("✅ DSPy Signature creation works")
        
        # Check if we have API access for LM
        api_key = os.getenv('A1_RESEARCH_API_KEY') or os.getenv('ANTHROPIC_API_KEY')
        if api_key:
            print("✅ API key available for LM integration")
        else:
            print("⚠️  No API key found - will need for LM operations")
        
        print("\n🎯 DSPy Setup Status: READY")
        print("Next: Design A1 signatures and modules")
        
    except ImportError as e:
        print(f"❌ DSPy import failed: {e}")
    except Exception as e:
        print(f"❌ Setup test failed: {e}")

if __name__ == "__main__":
    test_dspy_setup()