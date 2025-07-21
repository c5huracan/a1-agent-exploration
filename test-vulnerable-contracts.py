#!/usr/bin/env python3
"""
Test A1 Agent with Vulnerable Contracts
Compare LLM-guided analysis with known vulnerabilities
"""
import asyncio
import sys
import os
import time

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

from a1_agent import LLMInterface, A1Agent, TEST_CONTRACTS

# Expected vulnerabilities for each contract
EXPECTED_VULNERABILITIES = {
    "0x123": {  # VulnerableDeFiPool
        "reentrancy": "CRITICAL",
        "description": "State change after external call enables reentrancy"
    },
    "0x456": {  # ProxyContract
        "access_control": "HIGH",
        "proxy_risk": "HIGH",
        "description": "Access control and delegatecall proxy risks"
    },
    "0x789": {  # SimpleToken
        "vulnerabilities": None,
        "description": "Should be low risk"
    }
}

async def test_vulnerable_contracts():
    """Comprehensive test of A1 agent with vulnerable contracts"""
    print("🔬 A1 Agent Vulnerable Contract Analysis")
    print("=" * 50)
    print("🎯 Testing LLM-guided vulnerability detection")
    print("⏱️  Total time: ~3-4 minutes (includes rate limiting)")
    print()
    
    try:
        # Initialize A1 agent
        llm = LLMInterface(model="claude-3-5-haiku-20241022")
        agent = A1Agent(llm)
        
        results = {}
        
        for contract_address, contract_code in TEST_CONTRACTS.items():
            print(f"🎯 Analyzing {contract_address}")
            print("-" * 30)
            
            # Show expected vulnerabilities
            expected = EXPECTED_VULNERABILITIES.get(contract_address, {})
            if expected.get("vulnerabilities") is None:
                print("📋 Expected: LOW RISK (no major vulnerabilities)")
            else:
                print(f"📋 Expected: {expected.get('description', 'Various vulnerabilities')}")
            
            start_time = time.time()
            
            try:
                result = await agent.analyze_contract(contract_address, contract_code)
                end_time = time.time()
                
                # Store results
                results[contract_address] = result
                
                # Display detailed results
                print(f"⏱️  Analysis Time: {end_time - start_time:.1f}s")
                print(f"🔄 LLM Iterations: {result.iterations}")
                print(f"🛠️  Tools Selected: {', '.join(result.tool_usage)}")
                print(f"⚠️  Vulnerabilities Detected: {len(result.vulnerabilities)}")
                
                # Show vulnerabilities found
                if result.vulnerabilities:
                    for i, vuln in enumerate(result.vulnerabilities, 1):
                        severity_emoji = {
                            "CRITICAL": "🔴", 
                            "HIGH": "🟠", 
                            "MEDIUM": "🟡", 
                            "LOW": "🔵"
                        }.get(vuln["severity"], "⚪")
                        print(f"   {severity_emoji} {vuln['severity']}: {vuln['type']} - {vuln['description']}")
                else:
                    print("   ✅ No vulnerabilities detected")
                
                print(f"🎯 Risk Score: {result.risk_score}/10")
                print(f"🤖 LLM Analysis Preview: {result.reasoning[:150]}...")
                
                # Validation against expectations
                print("\n📊 Validation:")
                validate_results(contract_address, result, expected)
                
            except Exception as e:
                print(f"❌ Error analyzing {contract_address}: {e}")
                results[contract_address] = None
            
            print("\n" + "=" * 50 + "\n")
        
        # Summary analysis
        print_summary_analysis(results)
        
        # API usage summary  
        print(f"📊 API Usage Summary:")
        print(f"   Total Requests: {llm.request_count}")
        print(f"   Estimated Tokens: {llm.total_estimated_tokens}")
        print(f"   Estimated Cost: ${llm.total_estimated_tokens * 0.8 / 1000000:.4f}")
        print(f"   Cache Hits: {len(llm.response_cache)} unique responses cached")
        
    except Exception as e:
        print(f"❌ Fatal Error: {e}")

def validate_results(contract_address: str, result, expected: dict):
    """Validate A1 results against expected vulnerabilities"""
    detected_types = {vuln["type"] for vuln in result.vulnerabilities}
    
    if contract_address == "0x123":  # VulnerableDeFiPool
        if "reentrancy" in detected_types:
            print("   ✅ REENTRANCY correctly detected")
        else:
            print("   ❌ REENTRANCY missed - critical vulnerability not found")
        
        if result.risk_score >= 6.0:
            print(f"   ✅ HIGH RISK correctly assessed ({result.risk_score}/10)")
        else:
            print(f"   ⚠️  Risk score may be too low ({result.risk_score}/10)")
    
    elif contract_address == "0x456":  # ProxyContract
        proxy_detected = "proxy_risk" in detected_types
        access_detected = "access_control" in detected_types
        
        if proxy_detected:
            print("   ✅ PROXY RISKS correctly detected")
        else:
            print("   ❌ PROXY RISKS missed")
        
        if access_detected:
            print("   ✅ ACCESS CONTROL correctly detected")
        else:
            print("   ❌ ACCESS CONTROL missed")
    
    elif contract_address == "0x789":  # SimpleToken
        if len(result.vulnerabilities) <= 1 and result.risk_score <= 3.0:
            print("   ✅ LOW RISK correctly assessed")
        else:
            print(f"   ⚠️  May have false positives ({len(result.vulnerabilities)} vulns, {result.risk_score}/10)")

def print_summary_analysis(results: dict):
    """Print comprehensive summary of all results"""
    print("📋 COMPREHENSIVE ANALYSIS SUMMARY")
    print("=" * 50)
    
    total_vulns = 0
    total_critical = 0
    total_high = 0
    
    for address, result in results.items():
        if result:
            vulns = result.vulnerabilities
            total_vulns += len(vulns)
            total_critical += len([v for v in vulns if v["severity"] == "CRITICAL"])
            total_high += len([v for v in vulns if v["severity"] == "HIGH"])
            
            print(f"{address}: {len(vulns)} vulnerabilities, Risk {result.risk_score}/10")
    
    print(f"\n🎯 Detection Summary:")
    print(f"   Total Vulnerabilities: {total_vulns}")
    print(f"   Critical Issues: {total_critical}")  
    print(f"   High Risk Issues: {total_high}")
    
    print(f"\n🧠 LLM Decision Analysis:")
    for address, result in results.items():
        if result:
            print(f"   {address}: {result.iterations} iterations, tools: {result.tool_usage}")

if __name__ == "__main__":
    asyncio.run(test_vulnerable_contracts())